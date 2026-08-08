from pathlib import Path

from app.rag.document_loader import document_loader


PROJECT_ROOT = Path(__file__).resolve().parents[2]

KNOWLEDGE_BASE = PROJECT_ROOT / "knowledge_base"


def test_load_knowledge_documents():
    documents = [
        KNOWLEDGE_BASE / "raw" / "agriculture" / "Agriculture Schemes.docx",
        KNOWLEDGE_BASE / "raw" / "education" / "Education Schemes.docx",
        KNOWLEDGE_BASE / "raw" / "healthcare" / "HealthCare Schemes.docx",
    ]

    for file_path in documents:
        result = document_loader.load(file_path)

        assert result["file_name"]
        assert result["paragraphs"] or result["tables"]

        print(f"\nLoaded: {result['file_name']}")
        print(f"Paragraphs: {len(result['paragraphs'])}")
        print(f"Tables: {len(result['tables'])}")