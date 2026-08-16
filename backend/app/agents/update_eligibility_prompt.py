import re

with open('eligibility_agent.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add conversation history extraction
extraction_replacement = """        user_profile = state.get(
            "user_profile",
            {},
        )

        conversation_history = state.get(
            "conversation_history",
            [],
        )
        
        # Format conversation history for context
        history_text = ""
        if conversation_history:
            history_lines = []
            recent_history = conversation_history[-8:]
            for msg in recent_history:
                role = msg.get("role", "unknown").upper()
                msg_content = msg.get("content", "").strip()
                if msg_content:
                    history_lines.append(f"{role}: {msg_content}")
            history_text = "\\n".join(history_lines)

        available_documents = state.get(
            "available_documents",
            "",
        )"""

content = re.sub(
    r'        user_profile = state\.get\(\s*"user_profile",\s*\{\},\s*\)\s*available_documents = state\.get\(\s*"available_documents",\s*"",\s*\)',
    extraction_replacement,
    content
)

# Update user_prompt
prompt_replacement = """        user_prompt = f\"\"\"
CITIZEN PROFILE:

{json.dumps(user_profile, indent=2)}

RECENT CONVERSATION HISTORY (Use this to override or supplement profile info if user just provided it):

{history_text if history_text else "(No recent conversation)"}

CURRENT QUERY:
{query}

AVAILABLE DOCUMENTS (OCR EXTRACTED):

{available_documents if available_documents else "(No documents provided)"}

DOMAIN:

{domain}

VERIFIED SCHEME EVIDENCE:

{evidence_context}

Evaluate eligibility using ONLY the evidence above.

Follow these rules strictly:

1. Extract explicit eligibility requirements.

2. Compare EVERY requirement with the citizen profile AND the recent conversation history. If the user states a demographic detail in the history or current query (e.g., "I am male", "I am a farmer"), treat it as fact and use it to evaluate the rules.

3. If a required value is missing from the profile and conversation history,
   add it to missing_information.

4. If at least one required value is missing,
   status MUST be insufficient_information.

5. If at least one requirement is explicitly failed (based on profile OR conversation history),
   status MUST be not_eligible.

6. Status can be eligible ONLY if every explicit
   eligibility requirement is satisfied.

7. Do not assume missing information.

8. Do not treat scheme benefits as eligibility rules.

9. Do not use outside knowledge.

10. Do not mark a citizen eligible merely because
    one eligibility condition is satisfied.

11. If the official evidence explicitly says that
    eligibility criteria have NOT yet been notified,
    do NOT invent eligibility requirements.

12. In that situation, return insufficient_information
    and explain that the official eligibility criteria
    are not yet available.

13. Do not request agriculture-specific information
    for education or healthcare schemes unless the
    verified evidence explicitly requires it.

14. Do not request education-specific information
    for agriculture or healthcare schemes unless the
    verified evidence explicitly requires it.

15. Do not request healthcare-specific information
    for agriculture or education schemes unless the
    verified evidence explicitly requires it.

Return ONLY the required JSON.
\"\"\".strip()"""

content = re.sub(
    r'        user_prompt = f"""\s*CITIZEN PROFILE:.*?Return ONLY the required JSON.\s*"""\.strip\(\)',
    prompt_replacement,
    content,
    flags=re.DOTALL
)

with open('eligibility_agent.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated eligibility_agent.py")
