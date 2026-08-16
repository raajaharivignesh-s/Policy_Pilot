import asyncio
from app.graph.workflow import policy_pilot_workflow

async def run_test():
    conversation_history = []
    query = "What government schemes provide financial assistance for healthcare?"
    
    initial_state = {
        "query": query,
        "conversation_history": conversation_history,
        "user_profile": {},
    }
    
    config = {"configurable": {"thread_id": "test-thread-discovery"}}
    
    result = await policy_pilot_workflow.ainvoke(initial_state, config)
    
    print("----- RESULT -----")
    print("Intent:", result.get("intent"))
    print("Final Response (first 100 chars):")
    print(repr(result.get("final_response")[:100]))
    print("Recommendations length:", len(result.get("recommendations", [])))
    print("Supported information length:", len(result.get("supported_information", [])))

if __name__ == "__main__":
    asyncio.run(run_test())
