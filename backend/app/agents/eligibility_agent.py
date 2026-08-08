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
    """

    VALID_STATUSES = {
        "eligible",
        "not_eligible",
        "insufficient_information",
    }

    SYSTEM_PROMPT = """
You are the Eligibility Agent for PolicyPilot.

Your responsibility is to evaluate whether a citizen may
be eligible for government schemes using ONLY:

1. The citizen profile.
2. The verified scheme evidence supplied to you.

Do NOT use outside knowledge.

Do NOT invent eligibility rules.

Do NOT assume that missing information satisfies a rule.

For every scheme, return exactly one status:

- eligible
- not_eligible
- insufficient_information

IMPORTANT DECISION RULES:

1. If ANY mandatory eligibility requirement is missing
   from the citizen profile, the status MUST be:

   insufficient_information

2. If ANY explicit eligibility requirement is failed,
   the status MUST be:

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

9. Use only the supplied evidence.

10. If the evidence does not contain enough explicit
    eligibility information, return:

    insufficient_information

For every result:

- matched_rules must contain only rules explicitly
  satisfied by the citizen profile.

- failed_rules must contain only rules explicitly
  failed by the citizen profile.

- missing_information must contain required information
  that is absent from the citizen profile.

- reason must briefly explain the decision.

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
            "reason": "short explanation"
        }
    ]
}
""".strip()

    def __init__(self):
        self.llm_service = llm_service

    def run(
        self,
        state: PolicyPilotState,
    ) -> dict[str, Any]:

        user_profile = state.get(
            "user_profile",
            {},
        )

        verified_information = state.get(
            "verified_information",
            [],
        )

        # --------------------------------------------------
        # No verified information
        # --------------------------------------------------

        if not verified_information:
            return {
                "eligibility_results": [],
            }

        # --------------------------------------------------
        # Build evidence context
        # --------------------------------------------------

        evidence_parts = []

        for index, item in enumerate(
            verified_information,
            start=1,
        ):

            if item.get("supported") is False:
                continue

            scheme_name = item.get(
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

            evidence_parts.append(
                f"""
EVIDENCE {index}

Scheme:
{scheme_name}

Section:
{section}

Actual Evidence:
{evidence}

Verification Reason:
{reason}
""".strip()
            )

        if not evidence_parts:
            return {
                "eligibility_results": [],
            }

        evidence_context = "\n\n".join(
            evidence_parts
        )

        # --------------------------------------------------
        # Build LLM prompt
        # --------------------------------------------------

        user_prompt = f"""
CITIZEN PROFILE:

{json.dumps(user_profile, indent=2)}

VERIFIED SCHEME EVIDENCE:

{evidence_context}

Evaluate eligibility using ONLY the evidence above.

Follow these rules strictly:

1. Extract explicit eligibility requirements.

2. Compare EVERY requirement with the citizen profile.

3. If a required value is missing from the profile,
   add it to missing_information.

4. If at least one required value is missing,
   status MUST be insufficient_information.

5. If at least one requirement is explicitly failed,
   status MUST be not_eligible.

6. Status can be eligible ONLY if every explicit
   eligibility requirement is satisfied.

7. Do not assume missing information.

8. Do not treat scheme benefits as eligibility rules.

9. Do not use outside knowledge.

10. Do not mark a citizen eligible merely because
    one eligibility condition is satisfied.

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

        # --------------------------------------------------
        # Call LLM
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
                "eligibility_results": [],
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
            return {
                "eligibility_results": [],
                "errors": [
                    "Eligibility results must be a list."
                ],
            }

        # --------------------------------------------------
        # Validate and enforce eligibility status
        # --------------------------------------------------

        validated_results = []

        for result in results:

            if not isinstance(
                result,
                dict,
            ):
                continue

            scheme_name = result.get(
                "scheme_name",
                "",
            )

            if not scheme_name:
                continue

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

            # --------------------------------------------------
            # Normalize fields
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
            # Missing required information means the
            # citizen cannot be confirmed eligible.
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
            # Only allow eligible when there are:
            #
            # - no missing requirements
            # - no failed requirements
            # - at least one matched rule
            #
            # Otherwise force insufficient information.
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
            # Normalize invalid status
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
                    "scheme_name": scheme_name,
                    "status": status,
                    "matched_rules": matched_rules,
                    "failed_rules": failed_rules,
                    "missing_information": (
                        missing_information
                    ),
                    "reason": reason,
                }
            )

        return {
            "eligibility_results": validated_results,
        }


eligibility_agent = EligibilityAgent()