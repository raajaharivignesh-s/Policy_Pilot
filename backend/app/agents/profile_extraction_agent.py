import json
import logging
from typing import Any

from app.core.llm_json import parse_llm_json
from app.graph.state import PolicyPilotState
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

class ProfileExtractionAgent:
    """
    Extracts personal profile attributes (e.g., student status, age, gender, income)
    from the user's query and conversation history, updating the user_profile.
    """

    SYSTEM_PROMPT = """
You are a Profile Extraction Agent for PolicyPilot.
Your job is to read the user's question and conversation history, and extract any personal attributes the user has provided about themselves (e.g., age, gender, occupation, student status, income, caste).

You should ONLY return a JSON object with the extracted attributes. Do not modify or guess attributes that the user hasn't explicitly mentioned.
If the user hasn't mentioned any personal attributes, return an empty JSON object {}.

Common attributes to extract:
- "student": true/false
- "course": string (e.g. "B.Tech", "BA", "12th")
- "year_of_study": string (e.g. "1st year", "final year")
- "gender": string
- "age": number
- "income": number (annual income)
- "caste": string
- "occupation": string
- "institution_type": string (e.g. "government", "private")

Return exactly valid JSON. Example:
{
    "student": true,
    "course": "B.Tech",
    "year_of_study": "2nd year"
}
"""

    def __init__(self):
        self.llm_service = llm_service

    def run(self, state: PolicyPilotState) -> dict[str, Any]:
        query = state.get("query", "").strip()
        conversation_history = state.get("conversation_history", [])
        current_profile = state.get("user_profile", {})
        
        # If the query is too short and not part of an ongoing conversation, might not have attributes, 
        # but the LLM handles empty extraction well.

        history_text = "\n".join(
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in conversation_history[-6:]  # Only need recent context
            if msg.get("role") and msg.get("content")
        )

        user_prompt = f"CONVERSATION HISTORY:\n{history_text}\n\nCURRENT MESSAGE:\n{query}"

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT.strip()},
            {"role": "user", "content": user_prompt},
        ]

        response = self.llm_service.generate(messages=messages, temperature=0.0)

        try:
            extracted_data = parse_llm_json(response)
            if isinstance(extracted_data, dict):
                # Merge into current profile
                for k, v in extracted_data.items():
                    current_profile[k] = v
        except Exception as e:
            logger.error(f"Profile extraction failed: {e}")

        return {
            "user_profile": current_profile
        }

profile_extraction_agent = ProfileExtractionAgent()
