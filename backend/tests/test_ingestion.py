from pathlib import Path

from app.rag.ingestion import knowledge_ingestion


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


def test_knowledge_ingestion():

    results = knowledge_ingestion.process_documents(
        documents=DOCUMENTS
    )

    assert len(results) == 3

    total_chunks = 0

    for result in results:

        assert result["file_name"]
        assert result["domain"]
        assert result["chunks"]
        assert result["metadata"]

        assert (
            len(result["chunks"])
            == len(result["metadata"])
        )

        print("\n========================================")
        print("File:", result["file_name"])
        print("Domain:", result["domain"])
        print("Chunks:", result["chunk_count"])
        print("========================================")

        # Show the first chunk and metadata
        first_chunk = result["chunks"][0]
        first_metadata = result["metadata"][0]

        print("\nFirst chunk:")
        print(first_chunk.text)

        print("\nFirst metadata:")
        print(first_metadata)

        total_chunks += result["chunk_count"]

    print("\n========================================")
    print("TOTAL CHUNKS:", total_chunks)
    print("========================================")

    assert total_chunks > 0