import json
from typing import Any

from app.graph.state import PolicyPilotState
from app.services.llm_service import llm_service


class FinalResponseAgent:
    """
    Generates the final user-facing response.

    The agent uses only information that has already been
    produced and verified by the PolicyPilot workflow.

    It does NOT:
    - perform retrieval
    - perform eligibility decisions
    - invent scheme information
    - treat unsupported evidence as verified information
    """

    SYSTEM_PROMPT = """
You are the Final Response Agent for PolicyPilot,
a government-scheme assistance system.

Your task is to generate a clear, useful and concise
answer to the user's question.

IMPORTANT EVIDENCE POLICY:

1. Use ONLY the information supplied in the workflow context.
2. Do NOT use outside knowledge.
3. ONLY information with "supported": true may be presented
   as verified or confirmed information.
4. Information with "supported": false MUST NOT be presented
   as a confirmed government scheme, benefit, eligibility
   condition, amount, date or official announcement.
5. Do NOT turn unsupported web information into a factual
   government-scheme claim.
6. Do NOT invent government schemes, benefits, eligibility
   criteria, documents, amounts, dates or application steps.
7. Do NOT change the meaning of verified information.
8. If no supported information is available, clearly explain
   that the available information could not be sufficiently
   verified.
9. Never claim that a citizen is eligible unless the
   eligibility_results explicitly says "eligible".
10. Never claim that a citizen is not eligible unless the
    eligibility_results explicitly says "not_eligible".
11. If eligibility status is "insufficient_information",
    clearly explain that more information is required.
12. Keep the response easy to understand.
13. Use headings and bullet points when useful.
14. Do not mention internal agents, ChromaDB, embeddings,
    vector databases, prompts, LangGraph or internal workflow
    implementation details.
15. Answer the user's actual question directly.

SOURCE TRUST POLICY:

- HIGH trust information may be presented as verified when
  supported=true.
- MEDIUM trust information may be presented only according
  to the supplied verification result. Do not describe it
  as an official government source unless the supplied
  information explicitly establishes that.
- LOW trust information must never be presented as a
  confirmed government scheme or official policy.
- If all available web information is unsupported, clearly
  state that the information could not be verified from
  sufficiently trusted sources.

For scheme discovery:

- Present only recommended schemes.
- Recommendations must correspond to supported information.
- Explain why each recommended scheme is relevant using only
  the supplied recommendation information.
- If recommendations are empty, do not invent or list schemes.

For eligibility:

- Present the eligibility result.
- Mention matched rules, failed rules and missing information
  when available.
- Do not make your own eligibility decision.
- If eligibility is insufficient, clearly state what
  information is missing.

For unsupported/general questions:

- Clearly state that relevant government-scheme information
  was not found or could not be sufficiently verified.

Return ONLY the final user-facing response.
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

        intent = state.get(
            "intent",
            "",
        ).strip()

        domain = state.get(
            "domain",
            "",
        ).strip()

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
        # Keep only verified information
        # --------------------------------------------------

        supported_information = []

        for item in verified_information:

            if not isinstance(
                item,
                dict,
            ):
                continue

            if item.get(
                "supported",
                False,
            ) is not True:
                continue

            supported_information.append(
                item
            )

        # --------------------------------------------------
        # Keep only recommendations that correspond to
        # supported verified information.
        #
        # This gives us an additional safety boundary.
        # --------------------------------------------------

        supported_scheme_names = {
            item.get(
                "scheme_name",
                "",
            )
            for item in supported_information
            if item.get(
                "scheme_name",
                "",
            )
        }

        safe_recommendations = []

        for recommendation in recommendations:

            if not isinstance(
                recommendation,
                dict,
            ):
                continue

            scheme_name = recommendation.get(
                "scheme_name",
                "",
            )

            if (
                scheme_name
                and scheme_name in supported_scheme_names
            ):
                safe_recommendations.append(
                    recommendation
                )

        # --------------------------------------------------
        # Eligibility results are kept because they have
        # their own explicit status.
        # --------------------------------------------------

        safe_eligibility_results = []

        for result in eligibility_results:

            if not isinstance(
                result,
                dict,
            ):
                continue

            safe_eligibility_results.append(
                result
            )

        # --------------------------------------------------
        # Handle completely empty verified information
        # --------------------------------------------------

        if (
            not supported_information
            and not safe_recommendations
            and not safe_eligibility_results
        ):
            return {
                "final_response": (
                    "I couldn't find sufficiently verified "
                    "government scheme information to "
                    "answer this question reliably."
                )
            }

        # --------------------------------------------------
        # Build safe workflow context
        # --------------------------------------------------

        context = {
            "query": query,
            "intent": intent,
            "domain": domain,
            "verified_information": (
                supported_information
            ),
            "recommendations": (
                safe_recommendations
            ),
            "eligibility_results": (
                safe_eligibility_results
            ),
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
                    "VERIFIED WORKFLOW CONTEXT:\n"
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
                    "the available verified government "
                    "scheme information."
                )
            }

        return {
            "final_response": response,
        }


final_response_agent = FinalResponseAgent()