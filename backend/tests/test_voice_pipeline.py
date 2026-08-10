"""
Unit tests for voice pipeline — all OpenAI calls are mocked.
Tests STT, LLM streaming, TTS streaming, and sentence splitting.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Test: transcribe()
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_transcribe_empty_raises():
    from app.voice.pipeline import transcribe
    with pytest.raises(ValueError, match="No audio data"):
        await transcribe(b"")


@pytest.mark.asyncio
async def test_transcribe_calls_whisper():
    from app.voice.pipeline import transcribe

    mock_client = AsyncMock()
    mock_client.audio.transcriptions.create = AsyncMock(
        return_value="What schemes are available for farmers?"
    )

    with patch("app.voice.pipeline._make_async_client", return_value=mock_client):
        result = await transcribe(b"fake audio bytes", language="en")

    assert result == "What schemes are available for farmers?"
    mock_client.audio.transcriptions.create.assert_called_once()


# ---------------------------------------------------------------------------
# Test: sentence splitter
# ---------------------------------------------------------------------------

def test_split_into_sentences_basic():
    from app.voice.pipeline import split_into_sentences
    text = "Hello there. How are you? I am fine."
    sentences = split_into_sentences(text)
    assert len(sentences) == 3
    assert sentences[0] == "Hello there."


def test_split_into_sentences_single():
    from app.voice.pipeline import split_into_sentences
    sentences = split_into_sentences("No punctuation here")
    assert sentences == ["No punctuation here"]


def test_split_into_sentences_empty():
    from app.voice.pipeline import split_into_sentences
    assert split_into_sentences("") == []
    assert split_into_sentences("   ") == []


# ---------------------------------------------------------------------------
# Test: stream_llm_response()
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_stream_llm_response_yields_tokens():
    from app.voice.pipeline import stream_llm_response

    # Build a mock async iterator of chunks
    def make_chunk(content):
        choice = MagicMock()
        choice.delta.content = content
        chunk = MagicMock()
        chunk.choices = [choice]
        return chunk

    chunks = [make_chunk("PM"), make_chunk("-"), make_chunk("Kisan "), make_chunk("scheme.")]

    async def mock_iter():
        for c in chunks:
            yield c

    mock_stream = MagicMock()
    mock_stream.__aiter__ = lambda self: mock_iter()

    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_stream)

    tokens = []
    with patch("app.voice.pipeline._make_async_client", return_value=mock_client):
        async for token in stream_llm_response("What is PM-Kisan?"):
            tokens.append(token)

    assert "".join(tokens) == "PM-Kisan scheme."


# ---------------------------------------------------------------------------
# Test: run_voice_pipeline() — end-to-end with mocked providers
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_run_voice_pipeline_happy_path():
    from app.voice.pipeline import run_voice_pipeline

    # Mock STT
    async def mock_transcribe(audio_bytes, language=None):
        return "What schemes are available for farmers?"

    # Mock LLM streaming (yields tokens that form a sentence)
    async def mock_stream_llm(transcript, user_profile=None):
        for token in ["PM-Kisan provides Rs.", " 6000 per year for farmers."]:
            yield token

    # Mock TTS streaming (yields fake MP3 bytes)
    async def mock_stream_tts(sentence, voice):
        yield b"fake_mp3_header"
        yield b"fake_mp3_body"

    events = []
    binary_chunks = []

    with (
        patch("app.voice.pipeline.transcribe", side_effect=mock_transcribe),
        patch("app.voice.pipeline.stream_llm_response", side_effect=mock_stream_llm),
        patch("app.voice.pipeline.stream_tts_sentence", side_effect=mock_stream_tts),
    ):
        async for event in run_voice_pipeline(b"fake audio", voice="alloy"):
            if isinstance(event, bytes):
                binary_chunks.append(event)
            else:
                events.append(event)

    event_types = [e["type"] for e in events]

    assert "transcript" in event_types
    assert "response_start" in event_types
    assert "response" in event_types
    assert "response_end" in event_types
    assert "complete" in event_types

    # Verify transcript content
    transcript_event = next(e for e in events if e["type"] == "transcript")
    assert transcript_event["text"] == "What schemes are available for farmers?"

    # Verify complete event has latency
    complete_event = next(e for e in events if e["type"] == "complete")
    assert "latency_ms" in complete_event

    # Should have received MP3 binary chunks
    assert len(binary_chunks) > 0


@pytest.mark.asyncio
async def test_run_voice_pipeline_stt_failure():
    from app.voice.pipeline import run_voice_pipeline

    async def mock_fail_transcribe(audio_bytes, language=None):
        raise RuntimeError("Whisper API error")

    events = []
    with patch("app.voice.pipeline.transcribe", side_effect=mock_fail_transcribe):
        async for event in run_voice_pipeline(b"fake audio"):
            if isinstance(event, dict):
                events.append(event)

    assert any(e["type"] == "error" for e in events)
    error = next(e for e in events if e["type"] == "error")
    assert "STT failed" in error["message"]


@pytest.mark.asyncio
async def test_run_voice_pipeline_cancellation():
    """When cancel fires during LLM streaming, TTS audio should NOT start."""
    import asyncio
    from app.voice.pipeline import run_voice_pipeline

    cancel_event = asyncio.Event()

    async def mock_transcribe(audio_bytes, language=None):
        return "What is PM-Kisan?"

    async def mock_stream_llm(transcript, user_profile=None):
        # Signal cancellation before any text is yielded
        cancel_event.set()
        for token in ["Some", " text", " here"]:
            yield token

    async def mock_stream_tts(sentence, voice):
        yield b"chunk"

    events = []
    binary_chunks = []
    with (
        patch("app.voice.pipeline.transcribe", side_effect=mock_transcribe),
        patch("app.voice.pipeline.stream_llm_response", side_effect=mock_stream_llm),
        patch("app.voice.pipeline.stream_tts_sentence", side_effect=mock_stream_tts),
    ):
        async for event in run_voice_pipeline(
            b"fake audio",
            cancelled=cancel_event,
        ):
            if isinstance(event, bytes):
                binary_chunks.append(event)
            elif isinstance(event, dict):
                events.append(event)

    # Cancellation fires before min_chars threshold → TTS audio_start should NOT appear
    # and no binary audio chunks should have been sent
    assert not any(e["type"] == "audio_start" for e in events), (
        "TTS should not have started after cancellation"
    )
    assert len(binary_chunks) == 0, "No audio bytes should be sent after cancellation"
