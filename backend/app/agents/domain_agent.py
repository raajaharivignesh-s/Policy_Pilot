import json
from typing import Any

from app.graph.state import PolicyPilotState
from app.services.llm_service import llm_service


class DomainAgent:
    """
    Determines the knowledge domain relevant to the
    user's question.
    """

    VALID_DOMAINS = {
        "agriculture",
        "education",
        "healthcare",
        "general",
    }

    SYSTEM_PROMPT = """
You are the Domain Agent for PolicyPilot AI.

Your only responsibility is to identify the domain of the
user's question.

Supported domains:

1. agriculture
   Questions related to farmers, agriculture, crops,
   irrigation, farming assistance, agricultural schemes,
   and farmer benefits.

2. education
   Questions related to students, scholarships, education
   assistance, educational benefits, and student schemes.

3. healthcare
   Questions related to healthcare, medical treatment,
   health insurance, hospitals, maternity benefits,
   healthcare assistance, and health schemes.

4. general
   Questions that do not clearly belong to agriculture,
   education, or healthcare.

Return ONLY valid JSON in this exact format:

{
    "domain": "one_supported_domain"
}

Do not include explanations.
Do not use markdown.
Do not create new domain names.
""".strip()

    def __init__(self):
        self.llm_service = llm_service

    def classify(self, query: str) -> str:
        """
        Classify the query into one supported domain.
        """

        if not query or not query.strip():
            return "general"

        messages = [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": query.strip(),
            },
        ]

        response = self.llm_service.generate(
            messages=messages,
            temperature=0.0,
        )

        try:
            data: dict[str, Any] = json.loads(response)

            domain = data.get("domain")

            if domain in self.VALID_DOMAINS:
                return domain

        except (json.JSONDecodeError, TypeError):
            pass

        return "general"

    def run(
        self,
        state: PolicyPilotState,
    ) -> dict[str, Any]:
        """
        Execute domain classification and return the
        corresponding state update.
        """

        query = state.get("query", "")

        domain = self.classify(query)

        return {
            "domain": domain,
        }


domain_agent = DomainAgent()