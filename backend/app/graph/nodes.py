from app.graph.state import PolicyPilotState


def initialize_state(
    state: PolicyPilotState,
) -> PolicyPilotState:
    """
    Initialize and normalize the PolicyPilot workflow state.

    This node does not perform AI reasoning.
    It prepares the shared state for subsequent agents.
    """

    query = state.get("query", "").strip()

    return {
        **state,
        "query": query,
        "conversation_history": state.get(
            "conversation_history",
            [],
        ),
        "target_folder_id": state.get(
            "target_folder_id",
        ),
        "available_documents": state.get(
            "available_documents",
            "",
        ),
        "intent": state.get("intent", ""),
        "domain": state.get("domain", ""),
        "retrieved_documents": state.get(
            "retrieved_documents",
            [],
        ),
        "verified_information": state.get(
            "verified_information",
            [],
        ),
        "eligibility_results": state.get(
            "eligibility_results",
            [],
        ),
        "recommendations": state.get(
            "recommendations",
            [],
        ),
        "required_documents": state.get(
            "required_documents",
            [],
        ),
        "final_response": state.get(
            "final_response",
            "",
        ),
        "needs_clarification": state.get(
            "needs_clarification",
            False,
        ),
        "clarification_question": state.get(
            "clarification_question",
            "",
        ),
        "errors": state.get(
            "errors",
            [],
        ),
    }