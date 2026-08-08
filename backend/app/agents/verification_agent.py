import json
from typing import Any

from app.graph.state import PolicyPilotState
from app.services.llm_service import llm_service


class VerificationAgent:
    """
    Verifies whether retrieved knowledge provides sufficient
    support for the user's question.

    The agent preserves the original retrieved document
    content so downstream agents such as the Eligibility
    Agent can reason from the actual evidence.
    """

    SYSTEM_PROMPT = """
You are the Verification Agent for PolicyPilot AI.

Your responsibility is to evaluate retrieved government
scheme information against the user's question.

Use ONLY the supplied retrieved information.

Do not introduce facts from outside the supplied information.

For each retrieved document, determine whether it provides
useful information for answering the user's question.

Return ONLY valid JSON in this format:

{
    "verified_information": [
        {
            "scheme_name": "scheme name",
            "section": "section name",
            "supported": true,
            "reason": "short explanation"
        }
    ]
}

Rules:

- supported must be either true or false.
- Do not invent scheme names.
- Do not invent sections.
- Do not add information that is absent from the retrieved documents.
- Keep the reason short.
""".strip()

    def __init__(self):
        self.llm_service = llm_service

    def run(
        self,
        state: PolicyPilotState,
    ) -> dict[str, Any]:

        query = state.get(
            "query",
            "",
        ).strip()

        documents = state.get(
            "retrieved_documents",
            [],
        )

        # --------------------------------------------------
        # Validate query
        # --------------------------------------------------

        if not query:
            return {
                "verified_information": [],
                "errors": [
                    "Cannot verify information without a query."
                ],
            }

        # --------------------------------------------------
        # Validate retrieved documents
        # --------------------------------------------------

        if not documents:
            return {
                "verified_information": [],
            }

        # --------------------------------------------------
        # Build context for LLM
        # --------------------------------------------------

        context_parts = []

        for index, document in enumerate(
            documents,
            start=1,
        ):

            metadata = document.get(
                "metadata",
                {},
            )

            context_parts.append(
                f"""
DOCUMENT {index}

Scheme:
{metadata.get("scheme_name", "Unknown")}

Section:
{metadata.get("section", "Unknown")}

Domain:
{metadata.get("domain", "Unknown")}

Content:
{document.get("text", "")}
""".strip()
            )

        context = "\n\n".join(context_parts)

        # --------------------------------------------------
        # Build verification prompt
        # --------------------------------------------------

        user_prompt = f"""
USER QUESTION:

{query}

RETRIEVED INFORMATION:

{context}

Evaluate which retrieved documents actually support
answering the user's question.
""".strip()

        messages = [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]

        # --------------------------------------------------
        # Generate verification
        # --------------------------------------------------

        response = self.llm_service.generate(
            messages=messages,
            temperature=0.0,
        )

        # --------------------------------------------------
        # Parse LLM response
        # --------------------------------------------------

        try:
            data: dict[str, Any] = json.loads(response)

        except (json.JSONDecodeError, TypeError):

            return {
                "verified_information": [],
                "errors": [
                    "Verification Agent returned invalid JSON."
                ],
            }

        verified_information = data.get(
            "verified_information",
            [],
        )

        if not isinstance(
            verified_information,
            list,
        ):
            verified_information = []

        # --------------------------------------------------
        # Attach original evidence
        # --------------------------------------------------

        enriched_information = []

        for item in verified_information:

            if not isinstance(item, dict):
                continue

            scheme_name = item.get(
                "scheme_name",
                "",
            )

            section = item.get(
                "section",
                "",
            )

            if not scheme_name:
                continue

            if not section:
                continue

            # --------------------------------------------------
            # Find matching retrieved document
            # --------------------------------------------------

            source_document = None

            for document in documents:

                metadata = document.get(
                    "metadata",
                    {},
                )

                document_scheme = metadata.get(
                    "scheme_name",
                    "",
                )

                document_section = metadata.get(
                    "section",
                    "",
                )

                if (
                    document_scheme == scheme_name
                    and document_section == section
                ):
                    source_document = document
                    break

            # --------------------------------------------------
            # Preserve verification result
            # --------------------------------------------------

            enriched_item = {
                "scheme_name": scheme_name,
                "section": section,
                "supported": bool(
                    item.get(
                        "supported",
                        False,
                    )
                ),
                "reason": (
                    item.get(
                        "reason",
                        "",
                    )
                    if isinstance(
                        item.get(
                            "reason",
                            "",
                        ),
                        str,
                    )
                    else ""
                ),
            }

            # --------------------------------------------------
            # Add original retrieved evidence
            # --------------------------------------------------

            if source_document is not None:

                enriched_item["evidence"] = (
                    source_document.get(
                        "text",
                        "",
                    )
                )

                enriched_item["metadata"] = (
                    source_document.get(
                        "metadata",
                        {},
                    )
                )

            else:

                enriched_item["evidence"] = ""

                enriched_item["metadata"] = {}

            enriched_information.append(
                enriched_item
            )

        return {
            "verified_information": enriched_information,
        }


verification_agent = VerificationAgent()