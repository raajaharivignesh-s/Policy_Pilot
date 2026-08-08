from typing import Any

import chromadb

from app.core.settings import settings


class VectorService:
    """
    Handles storage and retrieval of document embeddings in ChromaDB.
    """

    COLLECTION_NAME = "government_schemes"

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_DB_PATH
        )

    def get_or_create_collection(self):
        return self.client.get_or_create_collection(
            name=self.COLLECTION_NAME
        )

    def add_documents(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]] | None = None,
    ) -> None:
        collection = self.get_or_create_collection()

        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def search(
        self,
        query_embedding: list[float],
        n_results: int = 5,
        where: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        collection = self.get_or_create_collection()

        return collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
        )

    def get(
        self,
        ids: list[str],
    ) -> dict[str, Any]:
        collection = self.get_or_create_collection()

        return collection.get(ids=ids)

    def delete(
        self,
        ids: list[str],
    ) -> None:
        collection = self.get_or_create_collection()

        collection.delete(ids=ids)

    def count(self) -> int:
        collection = self.get_or_create_collection()

        return collection.count()


vector_service = VectorService()