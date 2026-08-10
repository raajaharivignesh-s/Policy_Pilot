import asyncio
import io
import wave
from app.voice.pipeline import run_voice_pipeline

def create_dummy_wav():
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b'\x00\x00' * 16000) # 1 second silence
    return buf.getvalue()

async def main():
    print("Testing full pipeline live...")
    audio = create_dummy_wav()
    async for event in run_voice_pipeline(audio):
        if isinstance(event, dict):
            print("EVENT:", event)
        else:
            print(f"AUDIO CHUNK: {len(event)} bytes")

if __name__ == "__main__":
    asyncio.run(main())
