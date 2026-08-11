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

    Eligibility follow-up questions are generated directly
    from the EligibilityAgent's missing_information field.
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
    clearly state that more information is required.

12. Keep the response easy to understand.

13. Use headings and bullet points when useful.

14. Do not mention internal agents, ChromaDB, embeddings,
    vector databases, prompts, LangGraph or internal workflow
    implementation details.

15. Answer the user's actual question directly.

ELIGIBILITY FOLLOW-UP:

When eligibility_results contains:

    status = "insufficient_information"

and missing_information is not empty:

- Tell the user that eligibility cannot be confirmed yet.
- Explain that some information is missing.
- Ask the user to provide the missing information.
- Do not add requirements that are not present in
  missing_information.
- Do not claim the user is eligible or ineligible.

If missing_information is empty:

- Do not invent questions.
- Explain that eligibility could not be determined from
  the available verified information.

Return ONLY the final user-facing response.
""".strip()

    def __init__(self):
        self.llm_service = llm_service

    # ==========================================================
    # Convert missing information into questions
    # ==========================================================

    def _build_follow_up_questions(
        self,
        missing_information: list[Any],
    ) -> list[str]:
        """
        Convert missing_information into user-facing
        questions.

        No new requirements are created here.
        """

        questions: list[str] = []

        for item in missing_information:

            if not isinstance(
                item,
                str,
            ):
                continue

            item = item.strip()

            if not item:
                continue

            lower_item = item.lower()

            # --------------------------------------------------
            # Already a question
            # --------------------------------------------------

            if item.endswith("?"):

                question = item

            # --------------------------------------------------
            # "Is ..."
            # --------------------------------------------------

            elif lower_item.startswith("is "):

                question = (
                    item[0].upper()
                    + item[1:]
                    + "?"
                )

            # --------------------------------------------------
            # "Has ..."
            # --------------------------------------------------

            elif lower_item.startswith("has "):

                question = (
                    item[0].upper()
                    + item[1:]
                    + "?"
                )

            # --------------------------------------------------
            # "Have ..."
            # --------------------------------------------------

            elif lower_item.startswith("have "):

                question = (
                    item[0].upper()
                    + item[1:]
                    + "?"
                )

            # --------------------------------------------------
            # "Your ..."
            # --------------------------------------------------

            elif lower_item.startswith(
                "your "
            ):

                question = (
                    "What is "
                    + item
                    + "?"
                )

            # --------------------------------------------------
            # "Whether ..."
            # --------------------------------------------------

            elif lower_item.startswith(
                "whether "
            ):

                question = (
                    "Please confirm "
                    + item
                    + "."
                )

            # --------------------------------------------------
            # Generic missing information
            # --------------------------------------------------

            else:

                question = (
                    f"Please provide information "
                    f"about {item}."
                )

            if question not in questions:

                questions.append(
                    question
                )

        return questions

    # ==========================================================
    # Main Method
    # ==========================================================

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

        if not isinstance(
            recommendations,
            list,
        ):
            recommendations = []

        eligibility_results = state.get(
            "eligibility_results",
            [],
        )

        if not isinstance(
            eligibility_results,
            list,
        ):
            eligibility_results = []

        verified_information = state.get(
            "verified_information",
            [],
        )

        if not isinstance(
            verified_information,
            list,
        ):
            verified_information = []

        # ======================================================
        # 1. Filter supported information
        # ======================================================

        supported_information = [
            item
            for item in verified_information
            if (
                isinstance(
                    item,
                    dict,
                )
                and item.get(
                    "supported"
                ) is True
            )
        ]

        # ======================================================
        # 2. Handle eligibility follow-up
        # ======================================================

        if intent == "eligibility_check":

            for result in eligibility_results:

                if not isinstance(
                    result,
                    dict,
                ):
                    continue

                status = result.get(
                    "status",
                    "",
                )

                if status != (
                    "insufficient_information"
                ):
                    continue

                missing_information = (
                    result.get(
                        "missing_information",
                        [],
                    )
                )

                if not isinstance(
                    missing_information,
                    list,
                ):
                    missing_information = []

                questions = (
                    self._build_follow_up_questions(
                        missing_information
                    )
                )

                if questions:

                    scheme_name = str(
                        result.get(
                            "scheme_name",
                            "",
                        )
                    ).strip()

                    if scheme_name:

                        opening = (
                            "I can check your eligibility "
                            f"for {scheme_name}, but I "
                            "need a few more details first:"
                        )

                    else:

                        opening = (
                            "I can check your eligibility, "
                            "but I need a few more details "
                            "first:"
                        )

                    response_lines = [
                        opening,
                        "",
                    ]

                    for index, question in enumerate(
                        questions,
                        start=1,
                    ):

                        response_lines.append(
                            f"{index}. {question}"
                        )

                    response_lines.extend(
                        [
                            "",
                            (
                                "Please provide these "
                                "details so I can continue "
                                "the eligibility check."
                            ),
                        ]
                    )

                    return {
                        "final_response": (
                            "\n".join(
                                response_lines
                            )
                        ),
                        "needs_clarification": True,
                        "clarification_question": (
                            "\n".join(
                                questions
                            )
                        ),
                    }

                # --------------------------------------------------
                # Insufficient result but no explicit questions.
                #
                # Do NOT invent requirements.
                # --------------------------------------------------

                return {
                    "final_response": (
                        "I couldn't confirm your eligibility "
                        "from the available verified "
                        "government information yet. "
                        "Please provide any additional "
                        "scheme or citizen details you have "
                        "so the eligibility check can continue."
                    ),
                    "needs_clarification": True,
                    "clarification_question": (
                        "Please provide any additional "
                        "scheme or citizen details you have."
                    ),
                }

        # ======================================================
        # 3. No verified information
        # ======================================================

        if (
            not supported_information
            and not recommendations
            and not eligibility_results
        ):

            return {
                "final_response": (
                    "I couldn't find sufficiently verified "
                    "government scheme information to answer "
                    "this question reliably."
                ),
                "needs_clarification": False,
                "clarification_question": "",
            }

        # ======================================================
        # 4. Prepare safe recommendations
        # ======================================================

        safe_recommendations = []

        supported_scheme_names = {
            item.get(
                "scheme_name",
                "",
            )
            for item in supported_information
        }

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

            if scheme_name in supported_scheme_names:

                safe_recommendations.append(
                    recommendation
                )

        # ======================================================
        # 5. Build safe context
        # ======================================================

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
                eligibility_results
            ),
        }

        # ======================================================
        # 6. Generate normal final response
        # ======================================================

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

        # ======================================================
        # 7. Safe fallback
        # ======================================================

        if not response:

            return {
                "final_response": (
                    "I couldn't generate a response from "
                    "the available verified government "
                    "scheme information."
                ),
                "needs_clarification": False,
                "clarification_question": "",
            }

        return {
            "final_response": response,
            "needs_clarification": False,
            "clarification_question": "",
        }


final_response_agent = FinalResponseAgent()