import asyncio
import json
from app.graph.workflow import policy_pilot_workflow

async def run_test():
    conversation_history = [
        {"role": "user", "content": "What government schemes and scholarships are available for students?"},
        {"role": "assistant", "content": "Here are some schemes... 1. Scholarship for Differently Abled Students... 5. Tamizh Pudhalvan Scheme"},
        {"role": "user", "content": "am i eligible for 5th scheme"},
        {"role": "assistant", "content": "I can check your eligibility, but I need to verify your details. 1. Are you currently a student? 2. What is your course?"},
    ]
    query = "1. yes 2. B.tech computer technology 3. final year 4. Private college"
    
    initial_state = {
        "query": query,
        "conversation_history": conversation_history,
        "user_profile": {},
    }
    
    config = {"configurable": {"thread_id": "test-thread"}}
    
    result = await policy_pilot_workflow.ainvoke(initial_state, config)
    
    print("----- RESULT -----")
    print("Intent:", result.get("intent"))
    print("Domain:", result.get("domain"))
    
    # Print retrieved docs
    docs = result.get("retrieved_documents", [])
    print(f"Retrieved Docs: {len(docs)}")
    for d in docs:
        print("  -", d.get("metadata", {}).get("title", "Unknown Title"))
        
    # Print eligibility
    elig = result.get("eligibility_results", [])
    print("Eligibility Results:")
    print(json.dumps(elig, indent=2))
    
    # Print recommendations
    recs = result.get("recommendations", [])
    print("Recommendations:")
    for r in recs:
        print("  -", r.get("scheme_name"))

if __name__ == "__main__":
    asyncio.run(run_test())
