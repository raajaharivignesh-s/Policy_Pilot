from app.graph.state import PolicyPilotState


def route_after_verification(
    state: PolicyPilotState,
) -> str:
    """
    Decide which agent should execute after verification.
    """

    intent = state.get("intent", "").strip()

    # ----------------------------------------------
    # Eligibility questions
    # ----------------------------------------------

    if intent == "eligibility_check":
        return "eligibility_agent"

    # ----------------------------------------------
    # Scheme discovery questions
    # ----------------------------------------------

    if intent == "scheme_discovery":
        return "recommendation_agent"

    # ----------------------------------------------
    # All other intents
    # ----------------------------------------------

    return "final_response_agent"