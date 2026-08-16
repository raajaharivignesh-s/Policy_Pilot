import json
from typing import Any

from app.graph.state import PolicyPilotState
from app.services.llm_service import llm_service


class EligibilityAgent:
    """
    Evaluates citizen eligibility using:

    1. Citizen profile.
    2. Verified scheme evidence.

    Possible statuses:

        eligible
        not_eligible
        insufficient_information

    Important:

    - Uses only verified information.
    - Never invents eligibility rules.
    - Never assumes missing information.
    - If no verified eligibility evidence exists,
      returns insufficient_information.
    - Follow-up information requests are domain-aware.
    """

    VALID_STATUSES = {
        "eligible",
        "not_eligible",
        "insufficient_information",
    }

    ELIGIBILITY_SECTIONS = {
        "Eligibility Criteria",
        "Who Is Not Eligible",
        "Eligibility",
        "Eligibility Requirements",
    }

    SYSTEM_PROMPT = """
You are the Eligibility Agent for PolicyPilot.

Your responsibility is to evaluate whether a citizen may
be eligible for government schemes using ONLY:

1. The citizen profile.
2. The recent conversation history.
3. The available documents (OCR extracted text).
4. The verified scheme evidence supplied to you.

Do NOT use outside knowledge.

Do NOT invent eligibility rules.

Do NOT assume that missing information satisfies a rule.

For every scheme, return exactly one status:

- eligible
- not_eligible
- insufficient_information

IMPORTANT DECISION RULES:

1. If ANY mandatory eligibility requirement is missing
   from the citizen profile AND the available documents, the status MUST be:

   insufficient_information

2. If ANY explicit eligibility requirement is failed,
   status MUST be:

   not_eligible

3. The status may be eligible ONLY when ALL explicit
   eligibility requirements are satisfied.

4. Benefits are NOT eligibility rules.

5. Objectives are NOT eligibility rules.

6. Application processes are NOT eligibility rules.

7. Do not infer land ownership from occupation.

8. Do not infer income, age, citizenship, Aadhaar
   verification, bank account status, e-KYC status,
   family status, category, or any other missing value.
   Do NOT infer completion of previous education levels (e.g. 6-12th study)
   from a current degree/marksheet unless the document explicitly states it.

9. Use only the supplied evidence.

10. If the evidence does not contain enough explicit
    eligibility information, return:

    insufficient_information

For every result:

- matched_rules must contain only rules explicitly
  satisfied by the citizen profile or available documents.

- failed_rules must contain only rules explicitly
  failed by the citizen profile or available documents.

- missing_information must contain required information
  that is absent from the citizen profile AND available documents.

- reason must briefly explain the decision.

- required_documents must contain ONLY documents that are CURRENTLY MISSING. If a document is already provided in the available documents and satisfies a rule, do NOT include it in required_documents. Map only the missing_information to the documents needed to prove them.

Return ONLY valid JSON.

Required format:

{
    "eligibility_results": [
        {
            "scheme_name": "string",
            "status": "eligible",
            "matched_rules": [],
            "failed_rules": [],
            "missing_information": [],
            "reason": "short explanation",
            "required_documents": ["string"]
        }
    ]
}
""".strip()

    def __init__(self):
        self.llm_service = llm_service

    # ==========================================================
    # Helpers
    # ==========================================================

    def _get_scheme_name_from_query(
        self,
        query: str,
    ) -> str:
        """
        Try to identify the named scheme from the user query.

        This is intentionally lightweight.

        It does not invent a scheme name.

        It only extracts the text after common eligibility
        phrases such as:

            "Am I eligible for ..."
            "Tell me whether I am eligible for ..."
            "Can I apply for ..."
        """

        if not query:
            return ""

        normalized = query.strip()

        phrases = [
            "tell me whether i am eligible for",
            "tell me if i am eligible for",
            "am i eligible for",
            "are you eligible for",
            "is it possible for me to apply for",
            "can i apply for",
            "can i get",
            "eligibility for",
        ]

        lowered = normalized.lower()

        for phrase in phrases:

            if phrase in lowered:

                index = lowered.find(
                    phrase
                )

                scheme_name = normalized[
                    index + len(phrase):
                ]

                scheme_name = (
                    scheme_name
                    .strip()
                    .rstrip("?")
                    .strip()
                )

                if scheme_name:
                    return scheme_name

        return ""

    def _get_scheme_name_from_verified_information(
        self,
        verified_information: list[Any],
    ) -> str:
        """
        Return the first usable scheme name from verified
        information.

        Only verified information is considered.
        """

        for item in verified_information:

            if not isinstance(
                item,
                dict,
            ):
                continue

            if item.get(
                "supported"
            ) is not True:
                continue

            scheme_name = str(
                item.get(
                    "scheme_name",
                    "",
                )
            ).strip()

            if scheme_name:
                return scheme_name

        return ""

    def _get_domain_from_state(
        self,
        state: PolicyPilotState,
    ) -> str:
        """
        Return the normalized domain from workflow state.
        """

        domain = state.get(
            "domain",
            "",
        )

        if not isinstance(
            domain,
            str,
        ):
            return ""

        return domain.strip().lower()

    def _build_missing_information_from_profile(
        self,
        user_profile: dict[str, Any],
        domain: str,
    ) -> list[str]:
        """
        Build domain-aware information requests when the system
        knows that eligibility cannot yet be determined but
        does not have explicit eligibility rules to compare.

        IMPORTANT:

        These fields are NOT claimed to be official scheme
        eligibility requirements.

        They are only useful profile information that can help
        perform a later eligibility assessment.

        The questions are intentionally different for each
        PolicyPilot domain.

        Agriculture:
            - state
            - district
            - occupation
            - land ownership/cultivation
            - land details

        Education:
            - state
            - district
            - student status
            - course/program
            - year of study
            - institution type

        Healthcare:
            - state
            - district
            - age
            - occupation
            - income/family information

        Other domains:
            - state
            - district
        """

        if not isinstance(
            user_profile,
            dict,
        ):
            user_profile = {}

        domain = (
            domain
            or ""
        ).strip().lower()

        missing_information: list[str] = []

        # ======================================================
        # Common location information
        # ======================================================
        # Removed state and district since the app is exclusively for Tamil Nadu 
        # and schemes generally apply across all districts.

        # ======================================================
        # Agriculture
        # ======================================================

        if domain == "agriculture":

            if (
                "land_owner"
                not in user_profile
                and "land_acres"
                not in user_profile
                and "land_owner"
                not in user_profile
            ):
                missing_information.append(
                    (
                        "Whether you own or legally "
                        "cultivate agricultural land"
                    )
                )

            if not user_profile.get(
                "land_acres"
            ):
                missing_information.append(
                    (
                        "Your approximate agricultural "
                        "land or cultivation details"
                    )
                )

        # ======================================================
        # Education
        # ======================================================

        elif domain == "education":

            if not user_profile.get(
                "student"
            ) and not user_profile.get(
                "student_status"
            ):
                missing_information.append(
                    "Whether you are currently a student"
                )

            if not user_profile.get(
                "course"
            ) and not user_profile.get(
                "program"
            ):
                missing_information.append(
                    "Your course or program of study"
                )

            if not user_profile.get(
                "year"
            ) and not user_profile.get(
                "year_of_study"
            ) and not user_profile.get(
                "study_year"
            ):
                missing_information.append(
                    "Your current year of study"
                )

            if not user_profile.get(
                "institution_type"
            ):
                missing_information.append(
                    (
                        "Your institution type "
                        "(Government, Government-aided, "
                        "or Private)"
                    )
                )

        # ======================================================
        # Healthcare
        # ======================================================

        elif domain == "healthcare":

            if (
                "age"
                not in user_profile
                or user_profile.get(
                    "age"
                ) in (
                    None,
                    "",
                )
            ):
                missing_information.append(
                    "Your age"
                )

            if not user_profile.get(
                "occupation"
            ):
                missing_information.append(
                    "Your occupation"
                )

            if not user_profile.get(
                "annual_income"
            ) and not user_profile.get(
                "income"
            ):
                missing_information.append(
                    "Your approximate annual income"
                )

            if not user_profile.get(
                "family_size"
            ):
                missing_information.append(
                    "Your family size"
                )

        # ======================================================
        # General / unknown domain
        # ======================================================

        else:
            # Do not ask agriculture or other specific questions for general domain queries
            pass

        return missing_information

    # ==========================================================
    # Main Method
    # ==========================================================

    def run(
        self,
        state: PolicyPilotState,
    ) -> dict[str, Any]:

        user_profile = state.get(
            "user_profile",
            {},
        )

        conversation_history = state.get(
            "conversation_history",
            [],
        )
        
        # Format conversation history for context
        history_text = ""
        if conversation_history:
            history_lines = []
            recent_history = conversation_history[-8:]
            for msg in recent_history:
                role = msg.get("role", "unknown").upper()
                msg_content = msg.get("content", "").strip()
                if msg_content:
                    history_lines.append(f"{role}: {msg_content}")
            history_text = "\\n".join(history_lines)

        available_documents = state.get(
            "available_documents",
            "",
        )

        if not isinstance(
            user_profile,
            dict,
        ):
            user_profile = {}

        verified_information = state.get(
            "verified_information",
            [],
        )

        if not isinstance(
            verified_information,
            list,
        ):
            verified_information = []

        query = state.get(
            "query",
            "",
        ).strip()

        intent = state.get(
            "intent",
            "",
        ).strip()

        domain = self._get_domain_from_state(
            state
        )

        # ======================================================
        # Only eligibility queries should be evaluated here.
        # ======================================================

        if intent != "eligibility_check":

            return {
                "eligibility_results": [],
                "required_documents": [],
            }

        # ======================================================
        # Identify scheme name.
        # ======================================================

        scheme_name = (
            self._get_scheme_name_from_verified_information(
                verified_information
            )
        )

        if not scheme_name:

            scheme_name = (
                self._get_scheme_name_from_query(
                    query
                )
            )

        # ======================================================
        # Find supported verified information.
        # ======================================================

        supported_information = []

        for item in verified_information:

            if not isinstance(
                item,
                dict,
            ):
                continue

            if item.get(
                "supported"
            ) is not True:
                continue

            supported_information.append(
                item
            )

        # ======================================================
        # If no verified information exists at all,
        # return insufficient_information.
        #
        # The follow-up fields are domain-aware.
        # ======================================================

        if not supported_information:

            missing_information = (
                self._build_missing_information_from_profile(
                    user_profile,
                    domain,
                )
            )

            if not missing_information:

                missing_information = [
                    (
                        "The scheme-specific eligibility "
                        "information needed to assess your case"
                    )
                ]

            return {
                "eligibility_results": [
                    {
                        "scheme_name": scheme_name,
                        "status": (
                            "insufficient_information"
                        ),
                        "matched_rules": [],
                        "failed_rules": [],
                        "missing_information": (
                            missing_information
                        ),
                        "reason": (
                            "Eligibility cannot be confirmed "
                            "because sufficiently verified "
                            "scheme-specific eligibility "
                            "information is not available."
                        ),
                    }
                ],
                "required_documents": [],
            }

        # ======================================================
        # Build evidence context.
        # ======================================================

        evidence_parts = []

        for index, item in enumerate(
            supported_information,
            start=1,
        ):

            item_scheme_name = item.get(
                "scheme_name",
                "Unknown",
            )

            section = item.get(
                "section",
                "Unknown",
            )

            evidence = item.get(
                "evidence",
                "",
            )

            reason = item.get(
                "reason",
                "",
            )

            # --------------------------------------------------
            # Only eligibility-related evidence should be used
            # for eligibility decisions.
            # --------------------------------------------------

            if section not in self.ELIGIBILITY_SECTIONS:
                continue

            evidence_parts.append(
                f"""
EVIDENCE {index}

Scheme:
{item_scheme_name}

Section:
{section}

Actual Evidence:
{evidence}

Verification Reason:
{reason}
""".strip()
            )

        # ======================================================
        # No explicit eligibility evidence.
        # ======================================================

        if not evidence_parts:

            missing_information = (
                self._build_missing_information_from_profile(
                    user_profile,
                    domain,
                )
            )

            if not missing_information:

                missing_information = [
                    (
                        "The scheme-specific eligibility "
                        "information needed to assess your case"
                    )
                ]

            return {
                "eligibility_results": [
                    {
                        "scheme_name": scheme_name,
                        "status": (
                            "insufficient_information"
                        ),
                        "matched_rules": [],
                        "failed_rules": [],
                        "missing_information": (
                            missing_information
                        ),
                        "reason": (
                            "The available verified information "
                            "does not contain explicit eligibility "
                            "criteria sufficient to determine "
                            "eligibility."
                        ),
                    }
                ],
                "required_documents": [],
            }

        evidence_context = "\n\n".join(
            evidence_parts
        )

        # ======================================================
        # Build LLM prompt.
        # ======================================================

        user_prompt = f"""
CITIZEN PROFILE:

{json.dumps(user_profile, indent=2)}

RECENT CONVERSATION HISTORY (Use this to override or supplement profile info if user just provided it):

{history_text if history_text else "(No recent conversation)"}

CURRENT QUERY:
{query}

AVAILABLE DOCUMENTS (OCR EXTRACTED):

{available_documents if available_documents else "(No documents provided)"}

DOMAIN:

{domain}

VERIFIED SCHEME EVIDENCE:

{evidence_context}

Evaluate eligibility using ONLY the evidence above.

Follow these rules strictly:

1. Extract explicit eligibility requirements.

2. Compare EVERY requirement with the citizen profile, the recent conversation history, AND the available documents. If the user states a demographic detail in the history or current query (e.g., "I am male", "I am a farmer"), treat it as fact. If a document provides evidence (e.g., a Marksheet showing education, an Aadhaar card showing address/identity, an Enrollment Proof showing student status), treat it as fact. Use all of this to evaluate the rules.

3. If a required value is missing from the profile, conversation history, AND available documents,
   add it to missing_information.

4. If at least one required value is missing,
   status MUST be insufficient_information.

5. If at least one requirement is explicitly failed (based on profile, history, or documents),
   status MUST be not_eligible.

6. Status can be eligible ONLY if every explicit
   eligibility requirement is satisfied.

7. Do not assume missing information.

8. Do not treat scheme benefits as eligibility rules.

9. Do not use outside knowledge.

10. Do not mark a citizen eligible merely because
    one eligibility condition is satisfied.

11. If the official evidence explicitly says that
    eligibility criteria have NOT yet been notified,
    do NOT invent eligibility requirements.

12. In that situation, return insufficient_information
    and explain that the official eligibility criteria
    are not yet available.

13. Do not request agriculture-specific information
    for education or healthcare schemes unless the
    verified evidence explicitly requires it.

14. Do not request education-specific information
    for agriculture or healthcare schemes unless the
    verified evidence explicitly requires it.

15. Do not request healthcare-specific information
    for agriculture or education schemes unless the
    verified evidence explicitly requires it.

Return ONLY the required JSON.
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

        # ======================================================
        # Call LLM.
        # ======================================================

        response = self.llm_service.generate(
            messages=messages,
            temperature=0.0,
        )

        # ======================================================
        # Parse response.
        # ======================================================

        try:

            data: dict[str, Any] = json.loads(
                response
            )

        except (
            json.JSONDecodeError,
            TypeError,
        ):

            return {
                "eligibility_results": [
                    {
                        "scheme_name": scheme_name,
                        "status": (
                            "insufficient_information"
                        ),
                        "matched_rules": [],
                        "failed_rules": [],
                        "missing_information": [
                            (
                                "Additional information "
                                "required to evaluate eligibility"
                            )
                        ],
                        "reason": (
                            "Eligibility could not be "
                            "determined from the verified "
                            "evidence."
                        ),
                    }
                ],
                "required_documents": [],
                "errors": [
                    "Eligibility Agent returned invalid JSON."
                ],
            }

        results = data.get(
            "eligibility_results",
            [],
        )

        if not isinstance(
            results,
            list,
        ):
            results = []

        # ======================================================
        # Validate and enforce eligibility status.
        # ======================================================

        validated_results = []

        for result in results:

            if not isinstance(
                result,
                dict,
            ):
                continue

            result_scheme_name = str(
                result.get(
                    "scheme_name",
                    scheme_name,
                )
            ).strip()

            if not result_scheme_name:
                result_scheme_name = (
                    scheme_name
                )

            status = result.get(
                "status",
                "insufficient_information",
            )

            matched_rules = result.get(
                "matched_rules",
                [],
            )

            failed_rules = result.get(
                "failed_rules",
                [],
            )

            missing_information = result.get(
                "missing_information",
                [],
            )

            reason = result.get(
                "reason",
                "",
            )

            required_docs = result.get(
                "required_documents",
                [],
            )
            if not isinstance(required_docs, list):
                required_docs = []

            # --------------------------------------------------
            # Normalize fields.
            # --------------------------------------------------

            if not isinstance(
                matched_rules,
                list,
            ):
                matched_rules = []

            if not isinstance(
                failed_rules,
                list,
            ):
                failed_rules = []

            if not isinstance(
                missing_information,
                list,
            ):
                missing_information = []

            if not isinstance(
                reason,
                str,
            ):
                reason = ""

            # --------------------------------------------------
            # HARD SAFETY RULE 1
            #
            # Missing required information means eligibility
            # cannot be confirmed.
            # --------------------------------------------------

            if missing_information:

                status = (
                    "insufficient_information"
                )

                reason = (
                    "Eligibility cannot be confirmed "
                    "because required information is "
                    "missing from the citizen profile."
                )

            # --------------------------------------------------
            # HARD SAFETY RULE 2
            #
            # Explicitly failed requirements mean
            # not eligible.
            # --------------------------------------------------

            elif failed_rules:

                status = "not_eligible"

                reason = (
                    "The citizen does not satisfy "
                    "one or more explicit eligibility "
                    "requirements."
                )

            # --------------------------------------------------
            # HARD SAFETY RULE 3
            #
            # Eligible requires at least one explicit
            # matched rule and no missing/failed rules.
            # --------------------------------------------------

            elif (
                status == "eligible"
                and not matched_rules
            ):

                status = (
                    "insufficient_information"
                )

                reason = (
                    "Eligibility cannot be confirmed "
                    "because no explicit eligibility "
                    "requirement was matched."
                )

            # --------------------------------------------------
            # Normalize invalid status.
            # --------------------------------------------------

            elif status not in self.VALID_STATUSES:

                status = (
                    "insufficient_information"
                )

                reason = (
                    "Eligibility could not be "
                    "determined from the supplied evidence."
                )

            validated_results.append(
                {
                    "scheme_name": result_scheme_name,
                    "status": status,
                    "matched_rules": matched_rules,
                    "failed_rules": failed_rules,
                    "missing_information": (
                        missing_information
                    ),
                    "reason": reason,
                    "required_documents": required_docs,
                }
            )

        # ======================================================
        # LLM returned no usable result.
        # ======================================================

        if not validated_results:

            return {
                "eligibility_results": [
                    {
                        "scheme_name": scheme_name,
                        "status": (
                            "insufficient_information"
                        ),
                        "matched_rules": [],
                        "failed_rules": [],
                        "missing_information": [
                            (
                                "Additional information "
                                "required to evaluate eligibility"
                            )
                        ],
                        "reason": (
                            "Eligibility could not be "
                            "determined from the supplied "
                            "verified evidence."
                        ),
                    }
                ],
                "required_documents": [],
            }

        # Collect all unique required documents to return at top-level
        all_required_docs = []
        for r in validated_results:
            docs = r.get("required_documents", [])
            for doc in docs:
                if doc not in all_required_docs:
                    all_required_docs.append(doc)

        return {
            "eligibility_results": validated_results,
            "required_documents": all_required_docs,
        }


eligibility_agent = EligibilityAgent()