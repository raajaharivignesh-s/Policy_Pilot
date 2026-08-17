from app.services.openai_service import openai_service


class EmbeddingService:
    """
    Service responsible for generating text embeddings
    for documents and user queries.
    """

    def __init__(self):
        self.client = openai_service.navigate_client
        self.model = openai_service.get_embedding_model()

    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate an embedding for a single text.
        """

        response = self.client.embeddings.create(
            model=self.model,
            input=text,
        )

        return response.data[0].embedding

    def generate_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        """

        if not texts:
            return []

        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
        )

        return [item.embedding for item in response.data]


embedding_service = EmbeddingService()