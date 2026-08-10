"""
Voice AI Pipeline — Low-Latency Streaming

Architecture:
    Client audio chunks (binary WS frames)
        ↓ buffer
    END_OF_SPEECH signal
        ↓
    OpenAI Whisper STT  (transcribe buffered audio)
        ↓ transcript text
    PolicyPilot LLM  (stream=True, yields text chunks)
        ↓ text chunks (sentence-buffered)
    OpenAI TTS  (iter_bytes on each sentence)
        ↓ MP3 binary chunks
    Client WebSocket binary frames

Key latency optimisations:
  - LLM starts as soon as transcript arrives.
  - TTS starts on the FIRST complete sentence, not after full LLM response.
  - TTS audio bytes are sent immediately as they arrive from the API.
  - asyncio.create_task is used so TTS of sentence N overlaps with
    LLM generation of sentence N+1.
"""

import asyncio
import io
import re
import time
from collections.abc import AsyncGenerator
from typing import Any

from openai import AsyncOpenAI

from app.core.settings import settings


# ---------------------------------------------------------------------------
# OpenAI async client (voice-specific, lazy init for testability)
# ---------------------------------------------------------------------------

def _make_async_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
    )


# ---------------------------------------------------------------------------
# STT  — transcribe buffered audio bytes via Whisper
# ---------------------------------------------------------------------------

async def transcribe(
    audio_bytes: bytes,
    language: str | None = None,
) -> str:
    """
    Send buffered audio to Whisper and return the transcript text.
    Times the call and logs it for latency tracking.
    """
    if not audio_bytes:
        raise ValueError("No audio data to transcribe.")

    client = _make_async_client()
    buf = io.BytesIO(audio_bytes)

    # Detect format extension from magic bytes
    ext = "wav"
    if audio_bytes.startswith(b"\x1a\x45\xdf\xa3"):
        ext = "webm"
    elif audio_bytes.startswith(b"OggS"):
        ext = "ogg"
    elif audio_bytes.startswith(b"RIFF"):
        ext = "wav"
    elif audio_bytes.startswith(b"ID3") or audio_bytes.startswith(b"\xff\xfb") or audio_bytes.startswith(b"\xff\xf3"):
        ext = "mp3"
    elif b"ftyp" in audio_bytes[:32]:
        ext = "m4a"

    buf.name = f"audio.{ext}"

    t0 = time.perf_counter()

    kwargs: dict[str, Any] = {
        "model": settings.VOICE_STT_MODEL,
        "file": buf,
        "response_format": "text",
    }
    if language:
        kwargs["language"] = language

    raw_transcript = await client.audio.transcriptions.create(**kwargs)

    elapsed_ms = (time.perf_counter() - t0) * 1000

    # Extract text from string, dict, or object response
    transcript_text = ""
    if hasattr(raw_transcript, "text"):
        transcript_text = str(raw_transcript.text)
    elif isinstance(raw_transcript, dict):
        transcript_text = str(raw_transcript.get("text", ""))
    else:
        transcript_text = str(raw_transcript)

    raw_str = transcript_text.strip()
    if raw_str.startswith("{"):
        try:
            parsed = json.loads(raw_str)
            if isinstance(parsed, dict) and "text" in parsed:
                transcript_text = str(parsed["text"])
        except Exception:
            pass

    transcript_text = transcript_text.strip()
    print(f"[VOICE] STT latency: {elapsed_ms:.0f}ms — transcript: {transcript_text!r}")

    return transcript_text


# ---------------------------------------------------------------------------
from app.rag.context_builder import context_builder
from app.rag.retriever import retriever

# ---------------------------------------------------------------------------
# LLM — stream PolicyPilot response as text chunks
# ---------------------------------------------------------------------------

# Minimal system prompt for voice mode.
# The full multi-agent workflow is for typed queries via /api/v1/query.
# For voice, we use a direct streaming LLM call with the same expert role
# but optimised for spoken output (shorter, conversational sentences).
VOICE_SYSTEM_PROMPT = """
You are PolicyPilot Voice, an AI assistant that helps Indian citizens discover
and understand government schemes for agriculture, education and healthcare.

Keep your answers:
- Concise and conversational (spoken, not written).
- Factual — do not invent scheme names or amounts.
- Grounded in the provided knowledge base context.
- Structured as short sentences so they can be read aloud naturally.
- In the language the user is speaking (default: English).

If you don't know the answer or the context doesn't support it, say so clearly.
""".strip()


async def stream_llm_response(
    transcript: str,
    user_profile: dict[str, Any] | None = None,
) -> AsyncGenerator[str, None]:
    """
    Stream LLM text chunks grounded in the RAG Knowledge Base.
    Each yielded value is a small string fragment.
    Callers should buffer these into sentences before sending to TTS.
    """
    client = _make_async_client()

    # Retrieve grounding documents from ChromaDB vector service
    try:
        retrieved_docs = retriever.retrieve(transcript, top_k=3)
        kb_context = context_builder.build_context(retrieved_docs) if retrieved_docs else ""
    except Exception as exc:
        print(f"[VOICE] Knowledge base retrieval warning: {exc}")
        kb_context = ""

    profile_context = ""
    if user_profile:
        profile_context = f"\nUser profile: {user_profile}"

    system_prompt = VOICE_SYSTEM_PROMPT
    if kb_context:
        system_prompt += f"\n\nAUTHORITATIVE KNOWLEDGE BASE CONTEXT:\n{kb_context}\nAnswer using facts from the above context."

    t0 = time.perf_counter()
    first_token = True

    stream = await client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcript + profile_context},
        ],
        stream=True,
        temperature=0.2,
        max_tokens=400,        # Keep voice responses concise
    )

    async for chunk in stream:
        delta = chunk.choices[0].delta.content if chunk.choices else None
        if delta:
            if first_token:
                elapsed_ms = (time.perf_counter() - t0) * 1000
                print(f"[VOICE] LLM first token latency: {elapsed_ms:.0f}ms")
                first_token = False
            yield delta


# ---------------------------------------------------------------------------
# Sentence splitter — splits streaming text into TTS-ready sentences
# ---------------------------------------------------------------------------

# Sentence-ending punctuation patterns
_SENTENCE_END = re.compile(r'(?<=[.!?।])\s+')


def split_into_sentences(text: str) -> list[str]:
    """Split text on sentence boundaries, return non-empty sentences."""
    parts = _SENTENCE_END.split(text)
    return [p.strip() for p in parts if p.strip()]


# ---------------------------------------------------------------------------
# TTS — stream MP3 bytes for a text sentence
# ---------------------------------------------------------------------------

async def stream_tts_sentence(
    sentence: str,
    voice: str,
) -> AsyncGenerator[bytes, None]:
    """
    Stream TTS audio bytes for a single sentence.
    Yields raw MP3 chunks as they arrive.
    """
    client = _make_async_client()

    t0 = time.perf_counter()
    first_chunk = True

    async with client.audio.speech.with_streaming_response.create(
        model=settings.VOICE_TTS_MODEL,
        voice=voice,
        input=sentence,
        response_format="mp3",
        speed=1.0,
    ) as response:
        async for chunk in response.iter_bytes(chunk_size=1024):
            if chunk:
                if first_chunk:
                    elapsed_ms = (time.perf_counter() - t0) * 1000
                    print(f"[VOICE] TTS first chunk latency: {elapsed_ms:.0f}ms — sentence: {sentence[:40]!r}")
                    first_chunk = False
                yield chunk


# ---------------------------------------------------------------------------
# Full streaming pipeline — wires STT → LLM → TTS, yields events
# ---------------------------------------------------------------------------

async def run_voice_pipeline(
    audio_bytes: bytes | None = None,
    text_query: str | None = None,
    voice: str = "nova",
    language: str | None = None,
    user_profile: dict[str, Any] | None = None,
    cancelled: asyncio.Event | None = None,
) -> AsyncGenerator[dict | bytes, None]:
    """
    Full streaming voice/text pipeline.
    """
    pipeline_start = time.perf_counter()
    _cancelled = cancelled or asyncio.Event()

    # --------------------------------------------------------
    # 1. Obtain query text (via STT or text_query)
    # --------------------------------------------------------
    if text_query:
        transcript = text_query.strip()
    elif audio_bytes:
        try:
            transcript = await transcribe(audio_bytes, language=language)
        except Exception as exc:
            yield {"type": "error", "message": f"STT failed: {exc}"}
            return
    else:
        yield {"type": "error", "message": "Neither audio bytes nor text query was provided."}
        return

    if not transcript:
        yield {"type": "error", "message": "No query text detected."}
        return

    yield {"type": "transcript", "text": transcript}

    if _cancelled.is_set():
        return

    # --------------------------------------------------------
    # 2. LLM streaming → parallel sentence buffer → TTS streaming
    # --------------------------------------------------------
    yield {"type": "response_start"}

    min_chars = settings.VOICE_TTS_SENTENCE_MIN_CHARS
    event_queue: asyncio.Queue[dict | bytes | None] = asyncio.Queue()
    sentence_queue: asyncio.Queue[str | None] = asyncio.Queue()

    # Producer task: Stream LLM tokens, send text chunks immediately, push complete sentences to sentence_queue
    async def _llm_producer():
        sentence_buffer = ""
        try:
            async for token in stream_llm_response(transcript, user_profile=user_profile):
                if _cancelled.is_set():
                    break

                # Send text chunk to client immediately!
                await event_queue.put({"type": "response", "text": token})
                sentence_buffer += token

                # Check if sentence or clause boundary is reached
                if (
                    len(sentence_buffer) >= min_chars
                    and re.search(r'[.!?।,;:]\s*$', sentence_buffer)
                ):
                    await sentence_queue.put(sentence_buffer.strip())
                    sentence_buffer = ""

            if sentence_buffer.strip() and not _cancelled.is_set():
                await sentence_queue.put(sentence_buffer.strip())
                sentence_buffer = ""
        except Exception as exc:
            await event_queue.put({"type": "error", "message": f"LLM error: {exc}"})
        finally:
            await sentence_queue.put(None)  # Signal end of sentences to TTS task

    # Consumer task: Read sentences from sentence_queue and yield complete sentence TTS MP3 frames
    async def _tts_consumer():
        audio_started = False
        try:
            while not _cancelled.is_set():
                sentence = await sentence_queue.get()
                if sentence is None:
                    break
                if not sentence:
                    continue

                if not audio_started:
                    await event_queue.put({"type": "audio_start", "format": "mp3"})
                    audio_started = True

                sentence_bytes = bytearray()
                async for audio_chunk in stream_tts_sentence(sentence, voice=voice):
                    if _cancelled.is_set():
                        break
                    sentence_bytes.extend(audio_chunk)

                if sentence_bytes and not _cancelled.is_set():
                    await event_queue.put(bytes(sentence_bytes))
        except Exception as exc:
            await event_queue.put({"type": "error", "message": f"TTS error: {exc}"})
        finally:
            if audio_started:
                await event_queue.put({"type": "audio_end"})

    # Launch background tasks
    llm_task = asyncio.create_task(_llm_producer())
    tts_task = asyncio.create_task(_tts_consumer())

    # Helper task to close event_queue when both tasks finish
    async def _worker_supervisor():
        await asyncio.gather(llm_task, tts_task, return_exceptions=True)
        await event_queue.put(None)

    supervisor_task = asyncio.create_task(_worker_supervisor())

    # Yield all events from event_queue as they arrive
    while True:
        item = await event_queue.get()
        if item is None:
            break
        yield item

    yield {"type": "response_end"}

    total_ms = (time.perf_counter() - pipeline_start) * 1000
    print(f"[VOICE] Pipeline total latency: {total_ms:.0f}ms")

    yield {
        "type": "complete",
        "latency_ms": round(total_ms),
        "transcript": transcript,
    }
