"""
Standalone WebSocket Test Client for PolicyPilot Voice AI

Usage:
  1. Start backend server:
     cd backend
     $env:OPENAI_API_KEY="your_api_key"
     uvicorn app.main:app --reload --port 8000

  2. Run this test script:
     python test_ws_client.py path/to/sample_audio.wav
"""

import asyncio
import json
import sys
import websockets


WS_URL = "ws://127.0.0.1:8000/ws/voice"


async def test_voice_websocket(audio_file_path: str | None = None):
    print(f"Connecting to Voice WebSocket at {WS_URL} ...")

    async with websockets.connect(WS_URL) as ws:
        # 1. Receive greeting
        greeting = await ws.recv()
        print(f"\n[SERVER -> CLIENT] {greeting}")

        # 2. Optional configuration
        config_msg = {
            "type": "config",
            "voice": "alloy",
            "language": "en",
            "user_profile": {"occupation": "farmer", "state": "Tamil Nadu"}
        }
        await ws.send(json.dumps(config_msg))
        print(f"[CLIENT -> SERVER] Config sent: {config_msg['voice']}")

        ack = await ws.recv()
        print(f"[SERVER -> CLIENT] Config ack: {ack}")

        # 3. Stream audio bytes or send dummy speech payload
        if audio_file_path:
            print(f"\nStreaming audio file: {audio_file_path}")
            with open(audio_file_path, "rb") as f:
                chunk_size = 4096
                while chunk := f.read(chunk_size):
                    await ws.send(chunk)
                    await asyncio.sleep(0.01)
        else:
            print("\nNo audio file provided. Sending sample audio header bytes...")
            await ws.send(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80\x3e\x00\x00")

        # 4. Send end_of_speech signal
        eos_msg = {"type": "end_of_speech"}
        await ws.send(json.dumps(eos_msg))
        print("[CLIENT -> SERVER] Sent end_of_speech")

        # 5. Listen for streaming text events and binary MP3 audio chunks
        print("\n--- STREAMING RESPONSE START ---")
        received_audio_bytes = 0

        while True:
            try:
                message = await ws.recv()

                if isinstance(message, str):
                    event = json.loads(message)
                    event_type = event.get("type")

                    if event_type == "transcript":
                        print(f"\n[TRANSCRIPT]: {event['text']}\n[LLM RESPONSE STREAM]: ", end="", flush=True)

                    elif event_type == "response":
                        print(event.get("text", ""), end="", flush=True)

                    elif event_type == "audio_start":
                        print(f"\n\n[AUDIO STREAM START] Format: {event.get('format')}")

                    elif event_type == "audio_end":
                        print("\n[AUDIO STREAM END]")

                    elif event_type == "complete":
                        print(f"\n\n[COMPLETE] Total latency: {event.get('latency_ms')} ms")
                        break

                    elif event_type == "error":
                        print(f"\n\n[ERROR]: {event.get('message')}")
                        break

                elif isinstance(message, bytes):
                    received_audio_bytes += len(message)
                    print(".", end="", flush=True)

            except websockets.exceptions.ConnectionClosed:
                print("\n[DISCONNECTED]")
                break

        print(f"\nTotal audio bytes received: {received_audio_bytes} bytes")


if __name__ == "__main__":
    audio_path = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(test_voice_websocket(audio_path))
