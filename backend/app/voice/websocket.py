"""
Voice WebSocket Endpoint  —  /ws/voice

Protocol (client → server):
    Binary frames:  raw audio bytes (from browser MediaRecorder, webm/ogg/wav)
    Text frames:    JSON control messages

    Control messages:
        {"type": "config", "voice": "alloy", "language": "en", "user_profile": {}}
        {"type": "end_of_speech"}    → trigger STT + LLM + TTS pipeline
        {"type": "interrupt"}        → cancel current response generation
        {"type": "ping"}             → keepalive

Protocol (server → client):
    Text frames:    JSON events
        {"type": "connected", "session_id": "..."}
        {"type": "transcript", "text": "..."}
        {"type": "response_start"}
        {"type": "response", "text": "..."}   (LLM text chunks)
        {"type": "response_end"}
        {"type": "audio_start", "format": "mp3"}
        {"type": "audio_end"}
        {"type": "complete", "latency_ms": ..., "transcript": "..."}
        {"type": "error", "message": "..."}

    Binary frames:  raw MP3 audio chunks  (play directly in browser)
"""

import asyncio
import json
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.voice.pipeline import run_voice_pipeline


router = APIRouter(tags=["Voice AI (WebSocket)"])


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

class VoiceSession:
    """Holds per-connection state."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.audio_buffer: bytearray = bytearray()
        self.voice: str = "alloy"
        self.language: str | None = None
        self.user_profile: dict = {}
        # Set this to cancel the current response pipeline
        self.cancel_event: asyncio.Event = asyncio.Event()
        # Running pipeline task (if any)
        self.pipeline_task: asyncio.Task | None = None


# ---------------------------------------------------------------------------
# WebSocket endpoint
# ---------------------------------------------------------------------------

@router.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket):
    """
    Low-latency streaming voice endpoint.

    Lifecycle:
        connect → receive audio chunks → end_of_speech → stream response → loop
        interrupt → cancel current response → receive new audio → end_of_speech …
        disconnect → cleanup
    """
    await websocket.accept()

    session = VoiceSession(session_id=str(uuid.uuid4()))

    # Greet the client
    await _send_json(websocket, {
        "type": "connected",
        "session_id": session.session_id,
        "message": (
            "PolicyPilot Voice ready. "
            "Send audio chunks then {\"type\":\"end_of_speech\"} to process."
        ),
    })

    try:
        while True:
            message = await websocket.receive()

            # ----------------------------------------------------------------
            # Binary frame → audio chunk
            # ----------------------------------------------------------------
            if "bytes" in message and message["bytes"]:
                session.audio_buffer.extend(message["bytes"])
                continue

            # ----------------------------------------------------------------
            # Text frame → control message
            # ----------------------------------------------------------------
            if "text" not in message or not message["text"]:
                continue

            try:
                event = json.loads(message["text"])
            except json.JSONDecodeError:
                await _send_json(websocket, {
                    "type": "error",
                    "message": "Invalid JSON control message.",
                })
                continue

            msg_type = event.get("type", "")

            # ---- ping -------------------------------------------------------
            if msg_type == "ping":
                await _send_json(websocket, {"type": "pong"})
                continue

            # ---- config -----------------------------------------------------
            if msg_type == "config":
                session.voice = event.get("voice", "alloy")
                session.language = event.get("language") or None
                session.user_profile = event.get("user_profile") or {}
                await _send_json(websocket, {
                    "type": "config_ack",
                    "voice": session.voice,
                    "language": session.language,
                })
                continue

            # ---- interrupt --------------------------------------------------
            if msg_type == "interrupt":
                await _cancel_pipeline(session)
                session.audio_buffer = bytearray()
                await _send_json(websocket, {"type": "interrupted"})
                continue

            # ---- text_query --------------------------------------------------
            if msg_type == "text_query":
                text = event.get("text", "").strip()
                if not text:
                    await _send_json(websocket, {
                        "type": "error",
                        "message": "text parameter cannot be empty.",
                    })
                    continue

                await _cancel_pipeline(session)
                session.cancel_event = asyncio.Event()

                session.pipeline_task = asyncio.create_task(
                    _run_and_stream_pipeline(
                        websocket=websocket,
                        audio_bytes=None,
                        text_query=text,
                        session=session,
                    )
                )
                continue

            # ---- end_of_speech ----------------------------------------------
            if msg_type == "end_of_speech":
                if not session.audio_buffer:
                    await _send_json(websocket, {
                        "type": "error",
                        "message": "No audio received before end_of_speech.",
                    })
                    continue

                # Cancel any in-progress pipeline before starting a new one
                await _cancel_pipeline(session)

                # Snapshot and clear the audio buffer
                audio_snapshot = bytes(session.audio_buffer)
                session.audio_buffer = bytearray()

                # Fresh cancel event for this pipeline run
                session.cancel_event = asyncio.Event()

                # Run pipeline as a background task so we can receive
                # interrupt signals concurrently
                session.pipeline_task = asyncio.create_task(
                    _run_and_stream_pipeline(
                        websocket=websocket,
                        audio_bytes=audio_snapshot,
                        text_query=None,
                        session=session,
                    )
                )
                continue

            # ---- unknown ----------------------------------------------------
            await _send_json(websocket, {
                "type": "error",
                "message": f"Unknown message type: {msg_type!r}",
            })

    except WebSocketDisconnect:
        await _cancel_pipeline(session)
    except Exception as exc:
        try:
            await _send_json(websocket, {
                "type": "error",
                "message": f"Session error: {exc}",
            })
        except Exception:
            pass
        await _cancel_pipeline(session)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _send_json(ws: WebSocket, data: dict) -> None:
    """Send a JSON text frame, ignoring errors if socket is closed."""
    try:
        await ws.send_text(json.dumps(data))
    except Exception:
        pass


async def _send_bytes(ws: WebSocket, data: bytes) -> None:
    """Send a binary frame, ignoring errors if socket is closed."""
    try:
        await ws.send_bytes(data)
    except Exception:
        pass


async def _cancel_pipeline(session: VoiceSession) -> None:
    """Signal cancellation and wait for the task to finish."""
    session.cancel_event.set()
    if session.pipeline_task and not session.pipeline_task.done():
        session.pipeline_task.cancel()
        try:
            await session.pipeline_task
        except (asyncio.CancelledError, Exception):
            pass
    session.pipeline_task = None


async def _run_and_stream_pipeline(
    websocket: WebSocket,
    audio_bytes: bytes | None,
    text_query: str | None,
    session: VoiceSession,
) -> None:
    """
    Run the voice pipeline and forward every event to the WebSocket client.
    Text events go as JSON text frames; raw MP3 bytes as binary frames.
    """
    try:
        async for event in run_voice_pipeline(
            audio_bytes=audio_bytes,
            text_query=text_query,
            voice=session.voice,
            language=session.language,
            user_profile=session.user_profile,
            cancelled=session.cancel_event,
        ):
            if session.cancel_event.is_set():
                break

            if isinstance(event, bytes):
                await _send_bytes(websocket, event)
            elif isinstance(event, dict):
                await _send_json(websocket, event)

    except asyncio.CancelledError:
        pass
    except Exception as exc:
        await _send_json(websocket, {
            "type": "error",
            "message": f"Pipeline error: {exc}",
        })
