import asyncio
import json
from app.graph.workflow import policy_pilot_workflow

async def run_test():
    conversation_history = []
    query = "am i eligible for CMCHIS"
    
    initial_state = {
        "query": query,
        "conversation_history": conversation_history,
        "user_profile": {},
    }
    
    config = {"configurable": {"thread_id": "test-thread-cmchis"}}
    
    result = await policy_pilot_workflow.ainvoke(initial_state, config)
    
    print("----- RESULT -----")
    print("Intent:", result.get("intent"))
    print("Final Response:")
    print(result.get("final_response"))
    print("Required Docs:", result.get("required_documents"))

if __name__ == "__main__":
    asyncio.run(run_test())
