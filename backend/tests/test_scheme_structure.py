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


def test_scheme_structure():

    total_chunks = 0

    for domain, file_path in DOCUMENTS:

        print("\n")
        print("=" * 70)
        print(f"DOMAIN: {domain.upper()}")
        print(f"FILE: {file_path.name}")
        print("=" * 70)

        loaded = document_loader.load(file_path)

        raw_text = loaded["text"]

        cleaned_text = text_cleaner.clean(raw_text)

        chunks = scheme_chunker.chunk(
            text=cleaned_text,
            domain=domain,
        )

        assert chunks

        print(f"\nTotal chunks: {len(chunks)}")
        print("\nAll detected scheme names:\n")

        scheme_names = []

        for index, chunk in enumerate(chunks, start=1):

            if chunk.scheme_name not in scheme_names:
                scheme_names.append(chunk.scheme_name)

            print(
                f"{index:02d}. "
                f"Scheme: {chunk.scheme_name}"
            )
            print(
                f"    Section: {chunk.section}"
            )
            print(
                f"    Chunk ID: {chunk.chunk_id}"
            )
            print()

        print("-" * 70)
        print(
            f"UNIQUE SCHEMES: {len(scheme_names)}"
        )

        for index, scheme_name in enumerate(
            scheme_names,
            start=1,
        ):
            print(
                f"{index}. {scheme_name}"
            )

        total_chunks += len(chunks)

    print("\n")
    print("=" * 70)
    print(f"TOTAL CHUNKS ACROSS ALL DOMAINS: {total_chunks}")
    print("=" * 70)

    assert total_chunks > 0