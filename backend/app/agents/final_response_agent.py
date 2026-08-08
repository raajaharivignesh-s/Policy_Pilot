import json
from typing import Any

from app.graph.state import PolicyPilotState
from app.services.llm_service import llm_service


class FinalResponseAgent:
    """
    Generates the final user-facing response.

    The agent uses only information already produced by
    the PolicyPilot workflow.

    It does NOT:
    - perform retrieval
    - perform eligibility decisions
    - invent scheme information
    """

    SYSTEM_PROMPT = """
You are the Final Response Agent for PolicyPilot,
a government-scheme assistance system.

Your task is to generate a clear, useful and concise
answer to the user's question.

IMPORTANT RULES:

1. Use ONLY the information supplied in the workflow context.
2. Do NOT use outside knowledge.
3. Do NOT invent government schemes, benefits, eligibility
   criteria, documents, amounts, dates or application steps.
4. Do NOT change the meaning of verified information.
5. If the available information is insufficient, clearly
   say that the available knowledge base does not contain
   enough information.
6. Never claim that a citizen is eligible unless the
   eligibility_results explicitly says "eligible".
7. Never claim that a citizen is not eligible unless the
   eligibility_results explicitly says "not_eligible".
8. If eligibility status is "insufficient_information",
   clearly explain that more information is required.
9. Keep the response easy to understand.
10. Use headings and bullet points when useful.
11. Do not mention internal agents, ChromaDB, embeddings,
    vector databases, prompts, LangGraph or internal workflow
    implementation details.
12. Answer the user's actual question directly.

For scheme discovery:
- Present the relevant recommended schemes.
- Explain why each scheme is relevant using only the
  supplied recommendation information.

For eligibility:
- Present the eligibility result.
- Mention matched rules, failed rules and missing information
  when available.
- Do not make your own eligibility decision.

For unsupported/general questions:
- Clearly state that relevant government-scheme information
  was not found in the available knowledge base.

Return ONLY the final user-facing response.
""".strip()

    def __init__(self):
        self.llm_service = llm_service

    def run(
        self,
        state: PolicyPilotState,
    ) -> dict[str, Any]:

        query = state.get("query", "").strip()
        intent = state.get("intent", "").strip()
        domain = state.get("domain", "").strip()

        recommendations = state.get(
            "recommendations",
            [],
        )

        eligibility_results = state.get(
            "eligibility_results",
            [],
        )

        verified_information = state.get(
            "verified_information",
            [],
        )

        # --------------------------------------------------
        # Build workflow context
        # --------------------------------------------------

        context = {
            "query": query,
            "intent": intent,
            "domain": domain,
            "recommendations": recommendations,
            "eligibility_results": eligibility_results,
            "verified_information": verified_information,
        }

        # --------------------------------------------------
        # Handle empty workflow result without calling LLM
        # --------------------------------------------------

        if (
            not recommendations
            and not eligibility_results
            and not verified_information
        ):
            return {
                "final_response": (
                    "I couldn't find relevant government "
                    "scheme information in the available "
                    "knowledge base to answer this question."
                )
            }

        # --------------------------------------------------
        # Generate response
        # --------------------------------------------------

        messages = [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "USER QUESTION:\n"
                    f"{query}\n\n"
                    "WORKFLOW CONTEXT:\n"
                    f"{json.dumps(context, indent=2)}"
                ),
            },
        ]

        response = self.llm_service.generate(
            messages=messages,
            temperature=0.2,
        )

        response = response.strip()

        # --------------------------------------------------
        # Safe fallback
        # --------------------------------------------------

        if not response:
            return {
                "final_response": (
                    "I couldn't generate a response from "
                    "the available government scheme "
                    "information."
                )
            }

        return {
            "final_response": response,
        }


final_response_agent = FinalResponseAgent()