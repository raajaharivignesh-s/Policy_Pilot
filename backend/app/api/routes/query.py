from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.graph.workflow import policy_pilot_workflow
from app.services.profile_service import profile_service


router = APIRouter(
    prefix="/api/v1",
    tags=["PolicyPilot"],
)


# ============================================================
# Request Model
# ============================================================

class QueryRequest(BaseModel):
    """
    Request body for the PolicyPilot query endpoint.
    """

    query: str = Field(
        ...,
        min_length=1,
        description="Citizen's question",
    )

    user_id: str | None = Field(
        default=None,
        description="Citizen's PostgreSQL user ID",
    )

    user_profile: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Optional profile information. "
            "Used when user_id is not provided."
        ),
    )


# ============================================================
# Response Model
# ============================================================

class QueryResponse(BaseModel):
    """
    Response returned by the complete PolicyPilot workflow.
    """

    query: str

    intent: str

    domain: str

    retrieved_documents: list[dict[str, Any]]

    verified_information: list[dict[str, Any]]

    eligibility_results: list[dict[str, Any]]

    recommendations: list[dict[str, Any]]

    required_documents: list[str]

    final_response: str

    needs_clarification: bool

    clarification_question: str

    errors: list[str]


# ============================================================
# Query Endpoint
# ============================================================

@router.post(
    "/query",
    response_model=QueryResponse,
)
async def process_query(
    request: QueryRequest,
) -> QueryResponse:
    """
    Process a citizen's query through the complete
    PolicyPilot LangGraph workflow.
    """

    # --------------------------------------------------------
    # Validate query
    # --------------------------------------------------------

    query = request.query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )

    # --------------------------------------------------------
    # Load citizen profile
    # --------------------------------------------------------

    user_profile = request.user_profile

    if request.user_id:

        try:
            user_uuid = UUID(request.user_id)

        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail="Invalid user_id.",
            ) from exc

        try:
            database_profile = (
                profile_service.get_profile(
                    user_uuid
                )
            )

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="Failed to load citizen profile.",
            ) from exc

        if database_profile is None:
            raise HTTPException(
                status_code=404,
                detail="Citizen profile not found.",
            )

        user_profile = database_profile

    # --------------------------------------------------------
    # Build initial workflow state
    # --------------------------------------------------------

    initial_state = {
        "query": query,
        "user_profile": user_profile,
    }

    # --------------------------------------------------------
    # Execute complete LangGraph workflow
    # --------------------------------------------------------

    try:

        result = policy_pilot_workflow.invoke(
            initial_state
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail="Workflow execution failed.",
        ) from exc

    # --------------------------------------------------------
    # Validate workflow result
    # --------------------------------------------------------

    if not isinstance(
        result,
        dict,
    ):
        raise HTTPException(
            status_code=500,
            detail="Workflow returned an invalid response.",
        )

    # --------------------------------------------------------
    # Return structured API response
    # --------------------------------------------------------

    return QueryResponse(
        query=result.get(
            "query",
            query,
        ),
        intent=result.get(
            "intent",
            "",
        ),
        domain=result.get(
            "domain",
            "",
        ),
        retrieved_documents=result.get(
            "retrieved_documents",
            [],
        ),
        verified_information=result.get(
            "verified_information",
            [],
        ),
        eligibility_results=result.get(
            "eligibility_results",
            [],
        ),
        recommendations=result.get(
            "recommendations",
            [],
        ),
        required_documents=result.get(
            "required_documents",
            [],
        ),
        final_response=result.get(
            "final_response",
            "",
        ),
        needs_clarification=result.get(
            "needs_clarification",
            False,
        ),
        clarification_question=result.get(
            "clarification_question",
            "",
        ),
        errors=result.get(
            "errors",
            [],
        ),
    )