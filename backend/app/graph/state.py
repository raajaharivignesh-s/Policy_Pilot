from typing import Any, TypedDict


class PolicyPilotState(TypedDict, total=False):
    """
    Shared state for the complete PolicyPilot LangGraph workflow.

    Each agent reads the information it needs from this state
    and writes its results back into the state.
    """

    # ======================================================
    # User Input
    # ======================================================

    query: str

    # Structured information about the citizen.
    #
    # Example:
    #
    # {
    #     "age": 24,
    #     "occupation": "student",
    #     "income": 150000,
    #     "district": "Erode"
    # }
    user_profile: dict[str, Any]

    # ======================================================
    # Understanding
    # ======================================================

    intent: str

    domain: str

    # ======================================================
    # Knowledge Retrieval
    # ======================================================

    retrieved_documents: list[dict[str, Any]]

    # Information that has been checked against
    # retrieved knowledge / trusted sources.
    verified_information: list[dict[str, Any]]

    # ======================================================
    # Eligibility
    # ======================================================

    eligibility_results: list[dict[str, Any]]

    # ======================================================
    # Recommendation
    # ======================================================

    recommendations: list[dict[str, Any]]

    # ======================================================
    # Documents
    # ======================================================

    required_documents: list[str]

    # ======================================================
    # Final Response
    # ======================================================

    final_response: str

    # ======================================================
    # Workflow Control
    # ======================================================

    # Used when the workflow needs more information
    # from the citizen.
    needs_clarification: bool

    clarification_question: str

    # ======================================================
    # Error Handling
    # ======================================================

    errors: list[str]