"""
One-shot script to ingest all knowledge base documents into ChromaDB.
Run this from the backend/ directory:
    python ingest_knowledge_base.py
"""
import sys
from pathlib import Path

# Make sure backend/app is importable
sys.path.insert(0, str(Path(__file__).parent))

from app.rag.ingestion import knowledge_ingestion

KNOWLEDGE_BASE_ROOT = Path(__file__).parent.parent / "knowledge_base" / "raw"

DOCUMENTS = [
    ("agriculture", KNOWLEDGE_BASE_ROOT / "agriculture" / "Agriculture Schemes.docx"),
    ("education",   KNOWLEDGE_BASE_ROOT / "education"   / "Education Schemes.docx"),
    ("healthcare",  KNOWLEDGE_BASE_ROOT / "healthcare"  / "HealthCare Schemes.docx"),
]

def main():
    print("=" * 60)
    print("PolicyPilot Knowledge Base Ingestion")
    print("=" * 60)

    for domain, path in DOCUMENTS:
        if not path.exists():
            print(f"[SKIP] File not found: {path}")
            continue

        print(f"\n[INFO] Ingesting: {path.name}  (domain={domain})")
        result = knowledge_ingestion.process_document(
            file_path=path,
            domain=domain,
        )

        status = result.get("status", "unknown")
        chunks = result.get("chunk_count", 0)
        stored = result.get("stored_count", 0)

        if status == "success":
            print(f"  [OK]    {stored}/{chunks} chunks stored -- {path.name}")
        elif status == "no_chunks":
            print(f"  [WARN]  No chunks produced -- {path.name}")
        else:
            print(f"  [FAIL]  Failed -- {result}")

    print("\n" + "=" * 60)
    print("Ingestion complete! ChromaDB is ready.")
    print("=" * 60)

if __name__ == "__main__":
    main()
