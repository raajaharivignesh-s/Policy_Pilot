from app.rag.chunker import DocumentChunk


class MetadataBuilder:
    """
    Builds metadata for knowledge-base chunks.

    The generated metadata is used by the vector database
    for filtering, retrieval, source tracking, and
    scheme-level identification.
    """

    def build(
        self,
        chunk: DocumentChunk,
        source_file: str,
    ) -> dict[str, str]:
        """
        Build metadata for a single document chunk.
        """

        return {
            "scheme_name": chunk.scheme_name,
            "section": chunk.section,
            "domain": chunk.domain,
            "source_file": source_file,
            "source_type": "knowledge_base",
        }

    def build_many(
        self,
        chunks: list[DocumentChunk],
        source_file: str,
    ) -> list[dict[str, str]]:
        """
        Build metadata for multiple document chunks.
        """

        return [
            self.build(
                chunk=chunk,
                source_file=source_file,
            )
            for chunk in chunks
        ]


metadata_builder = MetadataBuilder()