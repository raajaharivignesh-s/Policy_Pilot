import json
from typing import Any

from app.graph.state import PolicyPilotState
from app.services.llm_service import llm_service


class IntentAgent:
    """
    Determines the user's intent from their question.

    This agent performs classification only.
    It does not perform retrieval, eligibility evaluation,
    recommendation, or final response generation.
    """

    VALID_INTENTS = {
        "scheme_discovery",
        "eligibility_check",
        "document_query",
        "scheme_information",
        "application_process",
        "general_query",
    }

    SYSTEM_PROMPT = """
You are the Intent Agent for PolicyPilot AI.

Your only responsibility is to classify the user's question
into exactly one supported intent.

Supported intents:

1. scheme_discovery
   The user wants to discover government schemes that may
   be relevant to them.

2. eligibility_check
   The user wants to know whether they qualify or may qualify
   for a particular government scheme.

3. document_query
   The user wants to know which documents are required.

4. scheme_information
   The user wants general information about a particular
   government scheme.

5. application_process
   The user wants to know how, where, or through which process
   they can apply for a scheme.

6. general_query
   The question does not clearly fit the above categories.

Return ONLY valid JSON in this exact format:

{
    "intent": "one_supported_intent"
}

Do not include explanations.
Do not include markdown.
Do not create new intent names.
""".strip()

    def __init__(self):
        self.llm_service = llm_service

    def classify(self, query: str) -> str:
        """
        Classify a user query into one supported intent.
        """

        if not query or not query.strip():
            return "general_query"

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

            intent = data.get("intent")

            if intent in self.VALID_INTENTS:
                return intent

        except (json.JSONDecodeError, TypeError):
            pass

        return "general_query"

    def run(
        self,
        state: PolicyPilotState,
    ) -> dict[str, Any]:
        """
        Execute the intent classification and return
        the state update.
        """

        query = state.get("query", "")

        intent = self.classify(query)

        return {
            "intent": intent,
        }


intent_agent = IntentAgent()