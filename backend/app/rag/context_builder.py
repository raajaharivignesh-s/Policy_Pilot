from dataclasses import dataclass

from app.rag.retriever import RetrievedDocument


@dataclass
class RAGContext:
    """
    Represents the structured context supplied to the LLM.
    """

    context: str
    documents: list[RetrievedDocument]


class ContextBuilder:
    """
    Converts retrieved knowledge chunks into a structured
    context for LLM generation.
    """

    def build(
        self,
        documents: list[RetrievedDocument],
    ) -> RAGContext:
        """
        Build a grounded context from retrieved documents.
        """

        if not documents:
            return RAGContext(
                context="",
                documents=[],
            )

        sections = []

        for index, document in enumerate(
            documents,
            start=1,
        ):
            metadata = document.metadata

            scheme_name = metadata.get(
                "scheme_name",
                "Unknown Scheme",
            )

            section = metadata.get(
                "section",
                "Unknown Section",
            )

            domain = metadata.get(
                "domain",
                "Unknown Domain",
            )

            source_file = metadata.get(
                "source_file",
                "Unknown Source",
            )

            sections.append(
                f"""
SOURCE {index}
Scheme: {scheme_name}
Section: {section}
Domain: {domain}
Source File: {source_file}

Content:
{document.text}
""".strip()
            )

        context = "\n\n".join(sections)

        return RAGContext(
            context=context,
            documents=documents,
        )


context_builder = ContextBuilder()