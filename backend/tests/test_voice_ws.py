"""
WebSocket connection tests for /ws/voice endpoint.
Tests connection lifecycle, control messages, and error handling.
"""

import asyncio
import json
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_app():
    """Import app fresh each test to avoid state bleed."""
    from app.main import app
    return app


# ---------------------------------------------------------------------------
# Test: WebSocket connects and receives 'connected' event
# ---------------------------------------------------------------------------

def test_voice_ws_connects():
    app = get_app()
    client = TestClient(app)

    with client.websocket_connect("/ws/voice") as ws:
        msg = ws.receive_json()
        assert msg["type"] == "connected"
        assert "session_id" in msg


# ---------------------------------------------------------------------------
# Test: ping → pong
# ---------------------------------------------------------------------------

def test_voice_ws_ping_pong():
    app = get_app()
    client = TestClient(app)

    with client.websocket_connect("/ws/voice") as ws:
        ws.receive_json()  # connected
        ws.send_json({"type": "ping"})
        pong = ws.receive_json()
        assert pong["type"] == "pong"


# ---------------------------------------------------------------------------
# Test: config message is acknowledged
# ---------------------------------------------------------------------------

def test_voice_ws_config_ack():
    app = get_app()
    client = TestClient(app)

    with client.websocket_connect("/ws/voice") as ws:
        ws.receive_json()  # connected
        ws.send_json({
            "type": "config",
            "voice": "nova",
            "language": "en",
            "user_profile": {"state": "Tamil Nadu"},
        })
        ack = ws.receive_json()
        assert ack["type"] == "config_ack"
        assert ack["voice"] == "nova"
        assert ack["language"] == "en"


# ---------------------------------------------------------------------------
# Test: end_of_speech with no audio → error
# ---------------------------------------------------------------------------

def test_voice_ws_end_of_speech_no_audio():
    app = get_app()
    client = TestClient(app)

    with client.websocket_connect("/ws/voice") as ws:
        ws.receive_json()  # connected
        ws.send_json({"type": "end_of_speech"})
        msg = ws.receive_json()
        assert msg["type"] == "error"
        assert "No audio received" in msg["message"]


# ---------------------------------------------------------------------------
# Test: invalid JSON → error
# ---------------------------------------------------------------------------

def test_voice_ws_invalid_json():
    app = get_app()
    client = TestClient(app)

    with client.websocket_connect("/ws/voice") as ws:
        ws.receive_json()  # connected
        ws.send_text("this is not json")
        msg = ws.receive_json()
        assert msg["type"] == "error"
        assert "Invalid JSON" in msg["message"]


# ---------------------------------------------------------------------------
# Test: unknown message type → error
# ---------------------------------------------------------------------------

def test_voice_ws_unknown_type():
    app = get_app()
    client = TestClient(app)

    with client.websocket_connect("/ws/voice") as ws:
        ws.receive_json()  # connected
        ws.send_json({"type": "unknown_cmd"})
        msg = ws.receive_json()
        assert msg["type"] == "error"
        assert "Unknown message type" in msg["message"]


# ---------------------------------------------------------------------------
# Test: full pipeline triggered by end_of_speech (mocked pipeline)
# ---------------------------------------------------------------------------

def test_voice_ws_full_pipeline_mocked():
    """
    Send audio chunks + end_of_speech and verify the pipeline events
    arrive on the WebSocket. All OpenAI calls are mocked.
    """
    app = get_app()
    client = TestClient(app)

    async def mock_pipeline(audio_bytes, voice, language, user_profile, cancelled):
        yield {"type": "transcript", "text": "What schemes are there for farmers?"}
        yield {"type": "response_start"}
        yield {"type": "response", "text": "PM-Kisan scheme provides support."}
        yield {"type": "response_end"}
        yield {"type": "audio_start", "format": "mp3"}
        yield b"\xff\xfb\x90\x00"  # fake MP3 header bytes
        yield {"type": "audio_end"}
        yield {"type": "complete", "latency_ms": 500, "transcript": "..."}

    with patch("app.voice.websocket.run_voice_pipeline", side_effect=mock_pipeline):
        with client.websocket_connect("/ws/voice") as ws:
            ws.receive_json()  # connected

            # Send fake audio binary chunks
            ws.send_bytes(b"fake audio chunk 1")
            ws.send_bytes(b"fake audio chunk 2")

            # Signal end of speech
            ws.send_json({"type": "end_of_speech"})

            # Collect events until complete
            received_events = []
            received_binary = []

            for _ in range(20):  # safety limit
                msg = ws.receive()
                if msg.get("text"):
                    event = json.loads(msg["text"])
                    received_events.append(event)
                    if event["type"] == "complete":
                        break
                elif msg.get("bytes"):
                    received_binary.append(msg["bytes"])

    event_types = [e["type"] for e in received_events]

    assert "transcript" in event_types
    assert "response_start" in event_types
    assert "response" in event_types
    assert "response_end" in event_types
    assert "audio_start" in event_types
    assert "audio_end" in event_types
    assert "complete" in event_types
    assert len(received_binary) > 0   # MP3 bytes arrived
