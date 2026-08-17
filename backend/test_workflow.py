import sys
import os

sys.path.insert(0, os.path.abspath("c:\\Users\\rajah\\OneDrive\\Desktop\\Policy-Pilot\\backend"))

from app.graph.workflow import policy_pilot_workflow

try:
    initial_state = {
        "query": "What government schemes are available for students?",
        "user_profile": {},
        "conversation_history": [],
        "target_folder_id": None,
        "available_documents": "",
        "extracted_document_fields": [],
    }
    config = {"configurable": {"thread_id": "test"}}
    result = policy_pilot_workflow.invoke(initial_state, config=config)
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
