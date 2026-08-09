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
    total_stored = 0

    for result in results:

        assert result["file_name"]
        assert result["file_path"]
        assert result["domain"]

        assert result["chunk_count"] >= 0
        assert result["stored_count"] >= 0

        assert result["status"] in {
            "success",
            "no_chunks",
        }

        if result["status"] == "success":

            assert result["chunk_count"] > 0

            assert (
                result["stored_count"]
                == result["chunk_count"]
            )

        print("\n========================================")
        print("File:", result["file_name"])
        print("Domain:", result["domain"])
        print("Chunk count:", result["chunk_count"])
        print("Stored count:", result["stored_count"])
        print("Status:", result["status"])
        print("========================================")

        total_chunks += result["chunk_count"]
        total_stored += result["stored_count"]

    print("\n========================================")
    print("TOTAL CHUNKS:", total_chunks)
    print("TOTAL STORED:", total_stored)
    print("========================================")

    assert total_chunks > 0
    assert total_stored == total_chunks