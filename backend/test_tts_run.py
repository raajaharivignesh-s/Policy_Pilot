import asyncio
from app.voice.pipeline import stream_tts_sentence

async def main():
    print("Testing stream_tts_sentence...")
    chunks = []
    async for chunk in stream_tts_sentence("Hello, welcome to Policy Pilot.", "alloy"):
        chunks.append(chunk)
    print(f"Chunks count: {len(chunks)}, Total bytes: {sum(len(c) for c in chunks)}")

if __name__ == "__main__":
    asyncio.run(main())
