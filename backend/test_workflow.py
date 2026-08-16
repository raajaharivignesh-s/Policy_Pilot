import asyncio
from app.graph.workflow import policy_pilot_workflow

async def main():
    initial_state = {
        "query": "check my eligibility",
        "user_profile": {},
        "conversation_history": [
            {"role": "user", "content": "explain TPS"},
            {"role": "assistant", "content": "The Tamizh Pudhalvan Scheme (TPS) provides..."}
        ],
        "target_folder_id": None,
        "available_documents": "",
        "extracted_document_fields": [],
    }

    config = {
        "configurable": {
            "thread_id": "test-123",
        }
    }

    try:
        result = policy_pilot_workflow.invoke(initial_state, config=config)
        print("Success!")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
