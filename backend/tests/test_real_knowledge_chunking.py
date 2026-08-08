from pathlib import Path

from app.rag.document_loader import document_loader
from app.rag.text_cleaner import text_cleaner
from app.rag.chunker import scheme_chunker


PROJECT_ROOT = Path(__file__).resolve().parents[2]

KNOWLEDGE_BASE = PROJECT_ROOT / "knowledge_base"


DOCUMENTS = [
    (
        "agriculture",
        KNOWLEDGE_BASE
        / "raw"
        / "agriculture"
        / "Agriculture Schemes.docx",
    ),
    (
        "education",
        KNOWLEDGE_BASE
        / "raw"
        / "education"
        / "Education Schemes.docx",
    ),
    (
        "healthcare",
        KNOWLEDGE_BASE
        / "raw"
        / "healthcare"
        / "HealthCare Schemes.docx",
    ),
]


def test_real_knowledge_chunking():
    total_chunks = 0

    for domain, file_path in DOCUMENTS:

        loaded = document_loader.load(file_path)

        raw_text = loaded["text"]

        cleaned_text = text_cleaner.clean(raw_text)

        chunks = scheme_chunker.chunk(
            text=cleaned_text,
            domain=domain,
        )

        assert chunks

        print("\n========================================")
        print(f"Domain: {domain}")
        print(f"File: {file_path.name}")
        print(f"Chunks generated: {len(chunks)}")
        print("========================================")

        # Print first chunk completely to verify
        # that table information is preserved.
        first_chunk = chunks[0]

        print("\nFirst chunk:")
        print(first_chunk.text)

        total_chunks += len(chunks)

    print("\n========================================")
    print(f"TOTAL CHUNKS: {total_chunks}")
    print("========================================")

    assert total_chunks > 0