from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from app.agents.domain_agent import domain_agent
from app.agents.eligibility_agent import eligibility_agent
from app.agents.final_response_agent import final_response_agent
from app.agents.intent_agent import intent_agent
from app.agents.recommendation_agent import recommendation_agent
from app.agents.research_agent import research_agent
from app.agents.verification_agent import verification_agent
from app.agents.profile_extraction_agent import profile_extraction_agent

from app.graph.nodes import initialize_state
from app.graph.router import route_after_verification
from app.graph.state import PolicyPilotState


def sync_understanding(state: PolicyPilotState):
    """
    Dummy node to synchronize parallel execution of understanding agents.
    """
    return {}


def route_after_domain(
    state: PolicyPilotState,
) -> str:
    """
    Decide whether the query requires knowledge retrieval
    after the domain has been identified.

    General/unrelated queries bypass the RAG pipeline.
    """

    domain = state.get(
        "domain",
        "",
    ).strip().lower()

    if domain in {
        "agriculture",
        "education",
        "healthcare",
    }:
        return "research_agent"

    return "final_response_agent"


def build_workflow():
    """
    Build the complete PolicyPilot LangGraph workflow.

    The workflow uses an InMemorySaver checkpointer so that
    state can be restored across multiple invocations using
    the same thread_id.

    Flow:

        START
          ↓
        initialize_state
          ↓
        intent_agent
          ↓
        domain_agent
          ↓
        domain router
             │
             ├── agriculture
             ├── education
             └── healthcare
                       ↓
                 research_agent
                       ↓
               verification_agent
                       ↓
                 intent router
                    │
             ┌──────┴────────┐
             │               │
        eligibility     scheme_discovery
             │               │
             ▼               ▼
        eligibility      recommendation
           agent              agent
             │               │
             └───────┬───────┘
                     ▼
             final_response_agent
                     │
                     ▼
                    END

        General/unrelated query:

        domain_agent
             ↓
        final_response_agent
             ↓
            END
    """

    graph = StateGraph(
        PolicyPilotState
    )

    # ==================================================
    # Nodes
    # ==================================================

    graph.add_node(
        "initialize_state",
        initialize_state,
    )

    graph.add_node(
        "profile_extraction_agent",
        profile_extraction_agent.run,
    )

    graph.add_node(
        "intent_agent",
        intent_agent.run,
    )

    graph.add_node(
        "domain_agent",
        domain_agent.run,
    )

    graph.add_node(
        "research_agent",
        research_agent.run,
    )

    graph.add_node(
        "verification_agent",
        verification_agent.run,
    )

    graph.add_node(
        "eligibility_agent",
        eligibility_agent.run,
    )

    graph.add_node(
        "recommendation_agent",
        recommendation_agent.run,
    )

    graph.add_node(
        "final_response_agent",
        final_response_agent.run,
    )

    graph.add_node(
        "sync_understanding",
        sync_understanding,
    )

    # ==================================================
    # START → Initialize
    # ==================================================

    graph.add_edge(
        START,
        "initialize_state",
    )

    # ==================================================
    # Main understanding pipeline (Parallel)
    # ==================================================

    graph.add_edge(
        "initialize_state",
        "profile_extraction_agent",
    )

    graph.add_edge(
        "initialize_state",
        "intent_agent",
    )

    graph.add_edge(
        "initialize_state",
        "domain_agent",
    )

    graph.add_edge(
        "profile_extraction_agent",
        "sync_understanding",
    )

    graph.add_edge(
        "intent_agent",
        "sync_understanding",
    )

    graph.add_edge(
        "domain_agent",
        "sync_understanding",
    )

    # ==================================================
    # Domain-based routing
    # ==================================================

    graph.add_conditional_edges(
        "sync_understanding",
        route_after_domain,
        {
            "research_agent": "research_agent",
            "final_response_agent": (
                "final_response_agent"
            ),
        },
    )

    # ==================================================
    # RAG pipeline
    # ==================================================

    graph.add_edge(
        "research_agent",
        "verification_agent",
    )

    # ==================================================
    # Intent-based routing after verification
    # ==================================================

    graph.add_conditional_edges(
        "verification_agent",
        route_after_verification,
        {
            "eligibility_agent": (
                "eligibility_agent"
            ),
            "recommendation_agent": (
                "recommendation_agent"
            ),
            "final_response_agent": (
                "final_response_agent"
            ),
        },
    )

    # ==================================================
    # Eligibility path
    # ==================================================

    graph.add_edge(
        "eligibility_agent",
        "final_response_agent",
    )

    # ==================================================
    # Recommendation path
    # ==================================================

    graph.add_edge(
        "recommendation_agent",
        "final_response_agent",
    )

    # ==================================================
    # Final response
    # ==================================================

    graph.add_edge(
        "final_response_agent",
        END,
    )

    # ==================================================
    # Checkpointer
    # ==================================================

    checkpointer = InMemorySaver()

    # ==================================================
    # Compile workflow with memory
    # ==================================================

    return graph.compile(
        checkpointer=checkpointer,
    )


policy_pilot_workflow = build_workflow()