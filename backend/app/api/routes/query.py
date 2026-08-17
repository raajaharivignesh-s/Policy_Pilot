from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.graph.workflow import policy_pilot_workflow
from app.services.profile_service import profile_service
from app.services.document_service import document_service
from app.services.document_requirement_service import (
    document_requirement_service,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["PolicyPilot"],
)


# ============================================================
# Server-side conversation history store
# ============================================================

# Maps conversation_id -> list of message dicts
# {"role": "user"|"assistant", "content": "..."}
_conversation_histories: dict[str, list[dict[str, str]]] = {}


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

    conversation_id: str | None = Field(
        default=None,
        description=(
            "Conversation identifier used to restore "
            "previous LangGraph state. Reuse the same "
            "conversation_id for follow-up questions."
        ),
    )

    conversation_history: list[dict[str, str]] = Field(
        default_factory=list,
        description=(
            "Optional conversation history from the "
            "frontend. If empty, the server will use "
            "its own accumulated history."
        ),
    )

    target_folder_id: str | None = Field(
        default=None,
        description="Target document folder ID for context.",
    )


# ============================================================
# Response Model
# ============================================================

class QueryResponse(BaseModel):
    """
    Response returned by the complete PolicyPilot workflow.
    """

    conversation_id: str

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

    The same conversation_id must be reused for
    follow-up questions so LangGraph can restore
    the previous workflow state.
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
    # Create or reuse conversation ID
    # --------------------------------------------------------

    if request.conversation_id:

        conversation_id = (
            request.conversation_id.strip()
        )

        if not conversation_id:

            conversation_id = str(
                uuid4()
            )

    else:

        conversation_id = str(
            uuid4()
        )

    # --------------------------------------------------------
    # Load citizen profile
    # --------------------------------------------------------

    user_profile = request.user_profile

    if request.user_id:

        try:

            user_uuid = UUID(
                request.user_id
            )

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
                detail=(
                    "Failed to load citizen profile."
                ),
            ) from exc

        # If a profile exists in the database, use it.
        # If not, continue with the default (empty)
        # profile — the user_id is still needed for
        # document loading even without a profile.
        if database_profile is not None:
            user_profile = database_profile

    # --------------------------------------------------------
    # Build conversation history
    #
    # Priority:
    #   1. Frontend-provided history (if non-empty)
    #   2. Server-side accumulated history
    # --------------------------------------------------------

    if request.conversation_history:
        conversation_history = list(
            request.conversation_history
        )
    else:
        conversation_history = list(
            _conversation_histories.get(
                conversation_id, []
            )
        )

    # --------------------------------------------------------
    # Build workflow initial state
    # --------------------------------------------------------
    
    available_documents_text = ""
    extracted_document_fields: list[dict[str, Any]] = []
    target_folder_id = request.target_folder_id

    if target_folder_id and request.user_id:
        try:
            folder_uuid = UUID(target_folder_id)
            user_uuid = UUID(request.user_id)

            extracted_document_fields = (
                document_service.get_structured_documents_in_folder(
                    folder_uuid,
                    user_uuid,
                )
            )

            if extracted_document_fields:
                available_documents_text = (
                    document_requirement_service.format_documents_for_prompt(
                        extracted_document_fields,
                        extracted_document_fields,
                    )
                )

                user_profile = (
                    document_requirement_service.merge_extracted_into_profile(
                        user_profile,
                        extracted_document_fields,
                    )
                )

        except ValueError:
            pass

    initial_state = {
        "query": query,
        "user_profile": user_profile,
        "conversation_history": conversation_history,
        "target_folder_id": target_folder_id,
        "available_documents": available_documents_text,
        "extracted_document_fields": extracted_document_fields,
    }

    # --------------------------------------------------------
    # LangGraph configuration
    #
    # The thread_id identifies the conversation.
    #
    # Reusing the same thread_id allows LangGraph to
    # restore the previous checkpoint.
    # --------------------------------------------------------

    config = {
        "configurable": {
            "thread_id": conversation_id,
        }
    }

    # --------------------------------------------------------
    # Execute complete LangGraph workflow
    # --------------------------------------------------------

    try:

        result = (
            policy_pilot_workflow.invoke(
                initial_state,
                config=config,
            )
        )

    except Exception as exc:
        import traceback
        with open("error.log", "a") as f:
            f.write("Workflow execution failed:\\n")
            traceback.print_exc(file=f)

        raise HTTPException(
            status_code=500,
            detail=(
                "Workflow execution failed."
            ),
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
            detail=(
                "Workflow returned an invalid response."
            ),
        )

    # --------------------------------------------------------
    # Accumulate conversation history server-side
    # --------------------------------------------------------

    final_response = result.get(
        "final_response",
        "",
    )

    if conversation_id not in _conversation_histories:
        _conversation_histories[conversation_id] = []

    _conversation_histories[conversation_id].append({
        "role": "user",
        "content": query,
    })

    if final_response:
        _conversation_histories[conversation_id].append({
            "role": "assistant",
            "content": final_response,
        })

    # Keep history bounded (last 20 messages = 10 turns)
    if len(_conversation_histories[conversation_id]) > 20:
        _conversation_histories[conversation_id] = (
            _conversation_histories[conversation_id][-20:]
        )

    # --------------------------------------------------------
    # Return structured API response
    # --------------------------------------------------------

    return QueryResponse(
        conversation_id=conversation_id,

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