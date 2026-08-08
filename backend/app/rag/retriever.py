from dataclasses import dataclass
from typing import Any

from app.services.embedding_service import embedding_service
from app.services.vector_service import vector_service


@dataclass
class RetrievedDocument:
    """
    Represents one document retrieved from ChromaDB.
    """

    text: str
    metadata: dict[str, Any]
    distance: float | None = None


class Retriever:
    """
    Retrieves relevant knowledge from ChromaDB
    using semantic similarity search.
    """

    MAX_DISTANCE = 1.25

    def __init__(self):
        self.embedding_service = embedding_service
        self.vector_service = vector_service

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        where: dict[str, Any] | None = None,
    ) -> list[RetrievedDocument]:
        """
        Retrieve relevant knowledge chunks.

        Results whose ChromaDB distance exceeds
        MAX_DISTANCE are discarded.
        """

        if not query or not query.strip():
            return []

        if top_k <= 0:
            return []

        # ----------------------------------------------
        # 1. Generate query embedding
        # ----------------------------------------------
        query_embedding = (
            self.embedding_service.generate_embedding(
                query.strip()
            )
        )

        # ----------------------------------------------
        # 2. Search ChromaDB
        # ----------------------------------------------
        results = self.vector_service.search(
            query_embedding=query_embedding,
            n_results=top_k,
            where=where,
        )

        # ----------------------------------------------
        # 3. Extract result lists
        # ----------------------------------------------
        documents = results.get("documents") or [[]]
        metadatas = results.get("metadatas") or [[]]
        distances = results.get("distances") or [[]]

        documents = documents[0] if documents else []
        metadatas = metadatas[0] if metadatas else []
        distances = distances[0] if distances else []

        retrieved_documents: list[RetrievedDocument] = []

        # ----------------------------------------------
        # 4. Apply similarity threshold
        # ----------------------------------------------
        for index, document in enumerate(documents):

            metadata = (
                metadatas[index]
                if index < len(metadatas)
                else {}
            )

            distance = (
                distances[index]
                if index < len(distances)
                else None
            )

            # If distance is unavailable, keep the result.
            if (
                distance is not None
                and distance > self.MAX_DISTANCE
            ):
                continue

            retrieved_documents.append(
                RetrievedDocument(
                    text=document,
                    metadata=metadata,
                    distance=distance,
                )
            )

        return retrieved_documents


retriever = Retriever()