import json
from typing import Any

from app.graph.state import PolicyPilotState
from app.services.llm_service import llm_service


class VerificationAgent:
    """
    Verifies whether retrieved information provides
    sufficient evidence for the user's question.

    The agent preserves:

    - original evidence
    - source metadata
    - source URL
    - source title
    - source trust level
    - source trust score

    The agent does not create new facts.
    """

    SYSTEM_PROMPT = """
You are the Verification Agent for PolicyPilot AI.

Your responsibility is to evaluate retrieved government
scheme information against the user's question.

Use ONLY the supplied retrieved information.

Do not introduce facts from outside the supplied information.

Each retrieved document has a source trust level:

HIGH:
Official government source. It can provide authoritative
support for a government scheme claim.

MEDIUM:
Reputable secondary or academic source. It can provide
supporting context but cannot independently establish an
official government policy claim.

LOW:
Unknown, private, aggregator, social media, or user-generated
source. It cannot independently establish that a government
scheme officially exists.

For each retrieved document, determine whether its content
actually provides useful evidence for the user's question.

Return ONLY valid JSON in this exact format:

{
    "verified_information": [
        {
            "document_index": 1,
            "supported": true,
            "reason": "short explanation"
        }
    ]
}

Rules:

- document_index must refer to the DOCUMENT number provided.
- supported must be either true or false.
- Do not invent document indexes.
- Do not invent scheme names.
- Do not invent sections.
- Do not add facts that are absent from the retrieved document.
- Do not treat a LOW trust source as authoritative evidence
  for an official government scheme.
- A MEDIUM trust source may provide supporting information,
  but it must not be described as an official government source.
- A HIGH trust source may provide authoritative support when
  its content directly supports the question.
- If the document does not actually support the question,
  mark supported as false.
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
        # Validate documents
        # --------------------------------------------------

        if not documents:
            return {
                "verified_information": [],
            }

        # --------------------------------------------------
        # Build context
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

Source Type:
{metadata.get("source_type", "knowledge_base")}

Source Trust Level:
{metadata.get("trust_level", "high")}

Source Trust Score:
{metadata.get("trust_score", 1.0)}

Trusted Source:
{metadata.get("trusted_source", True)}

Source Title:
{metadata.get("title", "")}

Source URL:
{metadata.get("url", "")}

Scheme:
{metadata.get("scheme_name", "")}

Section:
{metadata.get("section", "")}

Domain:
{metadata.get("domain", "")}

Content:
{document.get("text", "")}
""".strip()
            )

        context = "\n\n".join(
            context_parts
        )

        # --------------------------------------------------
        # Build verification prompt
        # --------------------------------------------------

        user_prompt = f"""
USER QUESTION:

{query}

RETRIEVED INFORMATION:

{context}

Evaluate which DOCUMENTS actually provide useful
supporting evidence for answering the question.

Pay particular attention to the source trust level.

Do not assume that a scheme is officially valid merely
because a low-trust website mentions it.
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
        # Parse response
        # --------------------------------------------------

        try:
            data: dict[str, Any] = json.loads(
                response
            )

        except (
            json.JSONDecodeError,
            TypeError,
        ):
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
        # Enrich using original documents
        # --------------------------------------------------

        enriched_information = []

        for item in verified_information:

            if not isinstance(
                item,
                dict,
            ):
                continue

            document_index = item.get(
                "document_index"
            )

            # --------------------------------------------------
            # Validate document index
            # --------------------------------------------------

            if not isinstance(
                document_index,
                int,
            ):
                continue

            if document_index < 1:
                continue

            if document_index > len(
                documents
            ):
                continue

            source_document = documents[
                document_index - 1
            ]

            metadata = source_document.get(
                "metadata",
                {},
            )

            # --------------------------------------------------
            # Source information
            # --------------------------------------------------

            source_type = metadata.get(
                "source_type",
                "knowledge_base",
            )

            source_url = metadata.get(
                "url",
                "",
            )

            source_title = metadata.get(
                "title",
                "",
            )

            trust_level = metadata.get(
                "trust_level",
                "high"
                if source_type == "knowledge_base"
                else "low",
            )

            trust_score = metadata.get(
                "trust_score",
                1.0
                if source_type == "knowledge_base"
                else 0.4,
            )

            trusted_source = metadata.get(
                "trusted_source",
                source_type == "knowledge_base",
            )

            scheme_name = metadata.get(
                "scheme_name",
                "",
            )

            section = metadata.get(
                "section",
                "",
            )

            reason = item.get(
                "reason",
                "",
            )

            if not isinstance(
                reason,
                str,
            ):
                reason = ""

            supported = bool(
                item.get(
                    "supported",
                    False,
                )
            )

            # --------------------------------------------------
            # Safety rule:
            #
            # LOW-trust web sources cannot independently
            # establish an official government claim.
            # --------------------------------------------------

            if (
                source_type == "web"
                and trust_level == "low"
            ):
                supported = False

            # --------------------------------------------------
            # Safety rule:
            #
            # A web result without identifiable evidence
            # cannot be treated as verified.
            # --------------------------------------------------

            evidence = source_document.get(
                "text",
                "",
            )

            if not evidence or not evidence.strip():
                supported = False

            # --------------------------------------------------
            # Build enriched result
            # --------------------------------------------------

            enriched_item = {
                "scheme_name": scheme_name,
                "section": section,
                "supported": supported,
                "reason": reason,
                "evidence": evidence,
                "metadata": metadata,
                "source_type": source_type,
                "source_url": source_url,
                "source_title": source_title,
                "trust_level": trust_level,
                "trust_score": trust_score,
                "trusted_source": bool(
                    trusted_source
                ),
            }

            enriched_information.append(
                enriched_item
            )

        return {
            "verified_information":
                enriched_information,
        }


verification_agent = VerificationAgent()