import json
import re
from typing import Any

from app.graph.state import PolicyPilotState
from app.services.llm_service import llm_service


class IntentAgent:
    """
    Determines the user's intent from their question.

    This agent performs classification only.

    It does not perform:
        - retrieval
        - eligibility evaluation
        - recommendation
        - verification
        - final response generation

    Important design rule:

        Explicit eligibility requests have the highest priority.

    Example:

        "What is Vetri Laptop Scheme, am I eligible for it?"

    must be classified as:

        eligibility_check

    even if the LLM initially classifies the query as
    scheme_information or scheme_discovery.
    """

    VALID_INTENTS = {
        "scheme_discovery",
        "eligibility_check",
        "document_query",
        "scheme_information",
        "application_process",
        "general_query",
    }

    # ==========================================================
    # Intent Priority
    # ==========================================================

    """
    Intent priority used for deterministic resolution.

    Highest priority:

        eligibility_check

    Then:

        document_query
        application_process
        scheme_information
        scheme_discovery
        general_query

    Eligibility is deliberately first because a query asking
    "am I eligible?" requires a completely different workflow
    from a normal scheme-information query.
    """

    SYSTEM_PROMPT = """
You are the Intent Agent for PolicyPilot AI.

Your only responsibility is to classify the user's question
into exactly one supported intent.

CRITICAL: When CONVERSATION HISTORY is provided, you MUST use
it to understand the context of the current question. Short
follow-up messages like "I am male", "yes", "3rd scheme" etc.
only make sense in context of the previous conversation.

Supported intents:

1. scheme_discovery

   The user wants to discover government schemes that may
   be relevant to them.

   Examples:
   - What government schemes are available for farmers?
   - What scholarships are available for students?
   - What schemes can help women?
   - (Follow-up) Suggest other schemes for me [when context shows ineligibility]

2. eligibility_check

   The user wants to know whether they qualify or may qualify
   for a particular government scheme.

   Examples:
   - Am I eligible for PM-KISAN?
   - Can I get the Vetri Laptop Scheme?
   - Do I qualify for Pudhumai Penn?
   - Am I eligible for this scheme?
   - (Follow-up) "I am male" [when previous context showed a women-only scheme]
   - (Follow-up) "I am 30 years old" [when eligibility was being checked]
   - (Follow-up) "Yes, I am a farmer" [responding to eligibility question]

   IMPORTANT:
   If the question contains an explicit eligibility request,
   such as "am I eligible", "do I qualify", "can I apply",
   or "am I entitled", classify it as eligibility_check.

   Also classify as eligibility_check when the user provides
   personal information (gender, age, occupation, income) as
   a follow-up to an eligibility discussion in history.

   This takes priority even when the same query also asks
   what the scheme is.

3. document_query

   The user wants to know which documents are required.

   Examples:
   - What documents do I need?
   - Which documents are required for PM-KISAN?

4. scheme_information

   The user wants general information about one particular
   government scheme.

   Examples:
   - What is PM-KISAN?
   - Tell me about Vetri Laptop Scheme.
   - What are the benefits of Pudhumai Penn?
   - (Follow-up) "Tell me about the 3rd scheme" [when schemes were listed]
   - (Follow-up) "Explain the second one" [when options were shown]

5. application_process

   The user wants to know how, where, or through which process
   they can apply for a scheme.

   Examples:
   - How do I apply for PM-KISAN?
   - Where can I apply?
   - What is the application process?

6. general_query

   The question does not clearly fit the above categories.

IMPORTANT PRIORITY RULE:

If a query contains BOTH:

    scheme information
    AND
    an explicit eligibility request

classify it as:

    eligibility_check

CONTEXT EXAMPLES:

History: [assistant showed 5 schemes for agriculture]
User: "Tell me more about the 3rd one"
Output: {"intent": "scheme_information"}

History: [assistant showed Pudhumai Penn scheme for women]
User: "I am male"
Output: {"intent": "eligibility_check"}

History: [assistant asked about income for PM-KISAN]
User: "My income is 2 lakhs per year"
Output: {"intent": "eligibility_check"}

Return ONLY valid JSON.

Exact format:

{
    "intent": "one_supported_intent"
}

Do not include explanations.
Do not include markdown.
Do not create new intent names.
""".strip()

    def __init__(self):
        self.llm_service = llm_service

    # ==========================================================
    # Text Normalization
    # ==========================================================

    def _normalize_text(
        self,
        text: str,
    ) -> str:
        """
        Normalize a query for deterministic intent detection.

        Examples:

            "Am I Eligible?"
                -> "am i eligible"

            "am-I-eligible?"
                -> "am i eligible"
        """

        if not text:
            return ""

        normalized = text.lower()

        normalized = re.sub(
            r"[^a-z0-9\s]",
            " ",
            normalized,
        )

        normalized = re.sub(
            r"\s+",
            " ",
            normalized,
        )

        return normalized.strip()

    # ==========================================================
    # Explicit Eligibility Detection
    # ==========================================================

    def _contains_explicit_eligibility_request(
        self,
        query: str,
    ) -> bool:
        """
        Detect explicit eligibility language.

        This deterministic check protects the workflow from
        an LLM incorrectly choosing scheme_information or
        scheme_discovery for an eligibility question.

        IMPORTANT:

        We intentionally do NOT use a broad word such as
        "eligible" alone because phrases need context.

        Examples that should return True:

            Am I eligible for PM-KISAN?
            Am I eligible?
            Do I qualify for Vetri Laptop?
            Can I get this scheme?
            Can I apply for this scheme?
            Am I entitled to this benefit?
            Tell me whether I am eligible.

        """

        normalized = self._normalize_text(
            query
        )

        if not normalized:
            return False

        eligibility_patterns = [
            r"\bam i eligible\b",
            r"\bam i qualify\b",
            r"\bdo i qualify\b",
            r"\bdo i qualify for\b",
            r"\bcan i qualify\b",
            r"\bcan i get\b",
            r"\bcan i receive\b",
            r"\bcan i avail\b",
            r"\bcan i benefit\b",
            r"\bcan i apply\b",
            r"\bcan i apply for\b",
            r"\bdo i meet the eligibility\b",
            r"\bdo i meet eligibility\b",
            r"\bdo i meet the criteria\b",
            r"\bdo i meet the requirements\b",
            r"\bam i entitled\b",
            r"\bam i eligible for\b",
            r"\bwhether i am eligible\b",
            r"\bwhether i qualify\b",
            r"\btell me if i am eligible\b",
            r"\btell me whether i am eligible\b",
            r"\bcheck my eligibility\b",
            r"\bcheck if i am eligible\b",
            r"\bcheck whether i am eligible\b",
            r"\beligibility for\b",
        ]

        return any(
            re.search(
                pattern,
                normalized,
            )
            for pattern in eligibility_patterns
        )

    # ==========================================================
    # Explicit Document Detection
    # ==========================================================

    def _contains_document_request(
        self,
        query: str,
    ) -> bool:
        """
        Detect explicit document-related requests.
        """

        normalized = self._normalize_text(
            query
        )

        document_patterns = [
            r"\bwhat documents\b",
            r"\bwhich documents\b",
            r"\bdocument required\b",
            r"\bdocuments required\b",
            r"\brequired documents\b",
            r"\bdocuments do i need\b",
            r"\bwhat proof\b",
            r"\bwhich proof\b",
            r"\bproof required\b",
            r"\bdocuments needed\b",
        ]

        return any(
            re.search(
                pattern,
                normalized,
            )
            for pattern in document_patterns
        )

    # ==========================================================
    # Explicit Application Detection
    # ==========================================================

    def _contains_application_request(
        self,
        query: str,
    ) -> bool:
        """
        Detect explicit application-process requests.
        """

        normalized = self._normalize_text(
            query
        )

        application_patterns = [
            r"\bhow do i apply\b",
            r"\bhow can i apply\b",
            r"\bwhere can i apply\b",
            r"\bwhere do i apply\b",
            r"\bhow to apply\b",
            r"\bapplication process\b",
            r"\bhow to register\b",
            r"\bwhere to register\b",
            r"\bregistration process\b",
            r"\bhow do i register\b",
        ]

        return any(
            re.search(
                pattern,
                normalized,
            )
            for pattern in application_patterns
        )

    # ==========================================================
    # Deterministic Intent Resolution
    # ==========================================================

    def _resolve_explicit_intent(
        self,
        query: str,
    ) -> str | None:
        """
        Resolve intent using deterministic rules before relying
        on the LLM.

        Priority:

            1. eligibility_check
            2. document_query
            3. application_process

        scheme_information and scheme_discovery are intentionally
        left to the LLM because their distinction is more
        semantic.
        """

        if self._contains_explicit_eligibility_request(
            query
        ):
            return "eligibility_check"

        if self._contains_document_request(
            query
        ):
            return "document_query"

        if self._contains_application_request(
            query
        ):
            return "application_process"

        return None

    # ==========================================================
    # LLM Classification
    # ==========================================================

    def _classify_with_llm(
        self,
        query: str,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> str:
        """
        Ask the LLM to classify the query.

        This is used only when deterministic rules do not
        already establish a higher-priority intent.

        When conversation_history is provided, it is injected
        into the prompt so the LLM can understand follow-up
        questions in context.
        """

        messages = [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT,
            },
        ]

        # Inject conversation history for context
        if conversation_history:
            history_text = "\n".join(
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in conversation_history
                if msg.get("role") and msg.get("content")
            )
            messages.append({
                "role": "user",
                "content": (
                    "CONVERSATION HISTORY:\n"
                    f"{history_text}\n\n"
                    "CURRENT QUESTION:\n"
                    f"{query.strip()}"
                ),
            })
        else:
            messages.append({
                "role": "user",
                "content": query.strip(),
            })

        try:

            response = self.llm_service.generate(
                messages=messages,
                temperature=0.0,
            )

        except Exception:
            return "general_query"

        try:

            data: dict[str, Any] = json.loads(
                response
            )

            intent = data.get(
                "intent"
            )

            if intent in self.VALID_INTENTS:
                return intent

        except (
            json.JSONDecodeError,
            TypeError,
        ):
            pass

        return "general_query"

    # ==========================================================
    # Public Classification
    # ==========================================================

    def classify(
        self,
        query: str,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> str:
        """
        Classify a user query into one supported intent.

        Explicit high-priority intents are resolved
        deterministically first.

        The LLM is used for the remaining semantic cases.
        """

        if not query or not query.strip():
            return "general_query"

        query = query.strip()

        # ------------------------------------------------------
        # Deterministic priority
        # ------------------------------------------------------

        explicit_intent = (
            self._resolve_explicit_intent(
                query
            )
        )

        if explicit_intent:
            return explicit_intent

        # ------------------------------------------------------
        # LLM classification
        # ------------------------------------------------------

        return self._classify_with_llm(
            query,
            conversation_history,
        )

    # ==========================================================
    # LangGraph Node
    # ==========================================================

    def run(
        self,
        state: PolicyPilotState,
    ) -> dict[str, Any]:
        """
        Execute intent classification and return the
        state update.
        """

        query = state.get(
            "query",
            "",
        )

        conversation_history = state.get(
            "conversation_history",
            [],
        )

        intent = self.classify(
            query,
            conversation_history,
        )

        return {
            "intent": intent,
        }


intent_agent = IntentAgent()