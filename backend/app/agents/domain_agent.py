import json
import re
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

    # ======================================================
    # Deterministic scheme-to-domain mapping
    # These take priority over the LLM to prevent
    # misclassification of known Tamil Nadu scheme names.
    # ======================================================

    SCHEME_DOMAIN_MAP = {
        # Education schemes
        "pudhalvan": "education",
        "pudhumai penn": "education",
        "tamizh pudhalvan": "education",
        "tamil pudhalvan": "education",
        "vetri laptop": "education",
        "post matric scholarship": "education",
        "post-matric scholarship": "education",
        "bc mbc dnc": "education",
        "minority post matric": "education",
        "scholarship": "education",
        "differently abled students": "education",

        # Agriculture schemes
        "pm kisan": "agriculture",
        "pm-kisan": "agriculture",
        "pmfby": "agriculture",
        "kuruvai": "agriculture",
        "crop insurance": "agriculture",
        "rythu bandhu": "agriculture",
        "micro irrigation": "agriculture",

        # Healthcare schemes
        "pm jay": "healthcare",
        "pm-jay": "healthcare",
        "ayushman bharat": "healthcare",
        "cmchis": "healthcare",
        "health insurance": "healthcare",
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
   assistance, educational benefits, student schemes,
   college, school, marksheet, study, course, degree.
   Specific schemes: Tamil Pudhalvan, Tamizh Pudhalvan,
   Pudhumai Penn, Vetri Laptop Scheme, Post-Matric
   Scholarship, BC/MBC/DNC Scholarship, Minority
   Post-Matric Scholarship.

3. healthcare
   Questions related to healthcare, medical treatment,
   health insurance, hospitals, maternity benefits,
   healthcare assistance, and health schemes.

4. general
   Questions that do not clearly belong to agriculture,
   education, or healthcare.

CRITICAL: Consider the CONVERSATION HISTORY context. If the
user was previously discussing education schemes and asks a
follow-up, classify it as "education".

Return ONLY valid JSON in this exact format:

{
    "domain": "one_supported_domain"
}

Do not include explanations.
Do not include markdown.
Do not create new domain names.
""".strip()

    def __init__(self):
        self.llm_service = llm_service

    def _deterministic_classify(self, query: str) -> str | None:
        """
        Try to classify the query deterministically by
        checking for known scheme names.
        Returns None if no match is found.
        """
        normalized = re.sub(r"[^a-z0-9\s]", " ", query.lower())
        normalized = re.sub(r"\s+", " ", normalized).strip()

        for scheme_key, domain in self.SCHEME_DOMAIN_MAP.items():
            if scheme_key in normalized:
                return domain

        return None

    def classify(self, query: str, conversation_history: list[dict[str, str]] = None) -> str:
        """
        Classify the query into one supported domain.
        Deterministic matching takes priority over LLM.
        """

        if not query or not query.strip():
            return "general"

        # 1. Try deterministic classification first
        deterministic_result = self._deterministic_classify(query)
        if deterministic_result:
            return deterministic_result

        # 2. Fall back to LLM classification
        history_text = ""
        if conversation_history:
            history_lines = []
            for msg in conversation_history[-6:]:
                role = msg.get("role", "unknown").upper()
                content = msg.get("content", "").strip()
                if content:
                    history_lines.append(f"{role}: {content}")
            history_text = "\n".join(history_lines)

        user_content = query.strip()
        if history_text:
            user_content = f"CONVERSATION HISTORY:\n{history_text}\n\nCURRENT QUERY: {query.strip()}"

        messages = [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_content,
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
        conversation_history = state.get("conversation_history", [])

        domain = self.classify(query, conversation_history)

        return {
            "domain": domain,
        }


domain_agent = DomainAgent()