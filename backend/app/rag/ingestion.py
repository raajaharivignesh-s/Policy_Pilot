from pathlib import Path
from typing import Any

from app.rag.document_loader import document_loader
from app.rag.text_cleaner import text_cleaner
from app.rag.chunker import scheme_chunker
from app.rag.metadata import metadata_builder
from app.services.embedding_service import embedding_service
from app.services.vector_service import vector_service


class KnowledgeIngestion:
    """
    Orchestrates the complete PolicyPilot knowledge ingestion pipeline.

    Pipeline:

        Document
            ↓
        Document Loader
            ↓
        Text Cleaner
            ↓
        Scheme Chunker
            ↓
        Metadata Builder
            ↓
        Embedding Service
            ↓
        ChromaDB / Vector Service
    """

    def process_document(
        self,
        file_path: str | Path,
        domain: str,
        batch_size: int = 20,
    ) -> dict[str, Any]:
        """
        Process one knowledge document and store its
        chunks and embeddings in the vector database.
        """

        path = Path(file_path)

        # --------------------------------------------------
        # 1. Load document
        # --------------------------------------------------
        loaded_document = document_loader.load(path)

        # --------------------------------------------------
        # 2. Get complete document text
        # --------------------------------------------------
        raw_text = loaded_document["text"]

        # --------------------------------------------------
        # 3. Clean text
        # --------------------------------------------------
        cleaned_text = text_cleaner.clean(raw_text)

        # --------------------------------------------------
        # 4. Create scheme-aware chunks
        # --------------------------------------------------
        chunks = scheme_chunker.chunk(
            text=cleaned_text,
            domain=domain,
        )

        if not chunks:
            return {
                "file_name": path.name,
                "file_path": str(path),
                "domain": domain,
                "chunk_count": 0,
                "stored_count": 0,
                "status": "no_chunks",
            }

        # --------------------------------------------------
        # 5. Build metadata
        # --------------------------------------------------
        metadata = metadata_builder.build_many(
            chunks=chunks,
            source_file=path.name,
        )

        # --------------------------------------------------
        # 6. Generate deterministic IDs
        # --------------------------------------------------
        ids = [
            chunk.chunk_id
            for chunk in chunks
        ]

        # --------------------------------------------------
        # 7. Remove existing vectors with the same IDs
        #
        # This makes ingestion safe to run again.
        # --------------------------------------------------
        vector_service.delete(ids)

        # --------------------------------------------------
        # 8. Generate embeddings and store in batches
        # --------------------------------------------------
        stored_count = 0

        for start in range(0, len(chunks), batch_size):

            end = start + batch_size

            batch_chunks = chunks[start:end]
            batch_metadata = metadata[start:end]
            batch_ids = ids[start:end]

            batch_documents = [
                chunk.text
                for chunk in batch_chunks
            ]

            # Generate embeddings
            batch_embeddings = (
                embedding_service.generate_embeddings(
                    batch_documents
                )
            )

            # Store in ChromaDB
            vector_service.add_documents(
                ids=batch_ids,
                documents=batch_documents,
                embeddings=batch_embeddings,
                metadatas=batch_metadata,
            )

            stored_count += len(batch_chunks)

        return {
            "file_name": path.name,
            "file_path": str(path),
            "domain": domain,
            "chunk_count": len(chunks),
            "stored_count": stored_count,
            "status": "success",
        }

    def process_documents(
        self,
        documents: list[tuple[str, str | Path]],
        batch_size: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Process multiple knowledge documents.

        Each item must contain:

            (domain, file_path)
        """

        results = []

        for domain, file_path in documents:

            result = self.process_document(
                file_path=file_path,
                domain=domain,
                batch_size=batch_size,
            )

            results.append(result)

        return results


knowledge_ingestion = KnowledgeIngestion()