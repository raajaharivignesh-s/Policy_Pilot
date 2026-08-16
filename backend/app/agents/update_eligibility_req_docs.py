import re

with open('eligibility_agent.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update SYSTEM_PROMPT to request required_documents
old_json_format = """{
    "eligibility_results": [
        {
            "scheme_name": "string",
            "status": "eligible",
            "matched_rules": [],
            "failed_rules": [],
            "missing_information": [],
            "reason": "short explanation"
        }
    ]
}"""

new_json_format = """{
    "eligibility_results": [
        {
            "scheme_name": "string",
            "status": "eligible",
            "matched_rules": [],
            "failed_rules": [],
            "missing_information": [],
            "reason": "short explanation",
            "required_documents": ["string"]
        }
    ]
}"""

content = content.replace(old_json_format, new_json_format)

# Also update the prompt rules description to mention required_documents extraction
old_instructions = """For every result:

- matched_rules must contain only rules explicitly
  satisfied by the citizen profile.

- failed_rules must contain only rules explicitly
  failed by the citizen profile.

- missing_information must contain required information
  that is absent from the citizen profile.

- reason must briefly explain the decision."""

new_instructions = """For every result:

- matched_rules must contain only rules explicitly
  satisfied by the citizen profile.

- failed_rules must contain only rules explicitly
  failed by the citizen profile.

- missing_information must contain required information
  that is absent from the citizen profile.

- reason must briefly explain the decision.

- required_documents must contain a list of document types required to apply for the scheme (e.g. "Aadhaar Card", "10th Marksheet", "Income Certificate", "Community Certificate", "Student ID proof") extracted from the verified scheme evidence."""

content = content.replace(old_instructions, new_instructions)

# 2. Update run method parsing logic
old_parse_section = """            missing_information = result.get(
                "missing_information",
                [],
            )

            reason = result.get(
                "reason",
                "",
            )"""

new_parse_section = """            missing_information = result.get(
                "missing_information",
                [],
            )

            reason = result.get(
                "reason",
                "",
            )

            required_docs = result.get(
                "required_documents",
                [],
            )
            if not isinstance(required_docs, list):
                required_docs = []"""

content = content.replace(old_parse_section, new_parse_section)

# Update validated_results append block
old_append_block = """            validated_results.append(
                {
                    "scheme_name": result_scheme_name,
                    "status": status,
                    "matched_rules": matched_rules,
                    "failed_rules": failed_rules,
                    "missing_information": (
                        missing_information
                    ),
                    "reason": reason,
                }
            )"""

new_append_block = """            validated_results.append(
                {
                    "scheme_name": result_scheme_name,
                    "status": status,
                    "matched_rules": matched_rules,
                    "failed_rules": failed_rules,
                    "missing_information": (
                        missing_information
                    ),
                    "reason": reason,
                    "required_documents": required_docs,
                }
            )"""

content = content.replace(old_append_block, new_append_block)

# Update return statement
old_return = """        return {
            "eligibility_results": validated_results,
        }"""

new_return = """        # Collect all unique required documents to return at top-level
        all_required_docs = []
        for r in validated_results:
            docs = r.get("required_documents", [])
            for doc in docs:
                if doc not in all_required_docs:
                    all_required_docs.append(doc)

        return {
            "eligibility_results": validated_results,
            "required_documents": all_required_docs,
        }"""

content = content.replace(old_return, new_return)

with open('eligibility_agent.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Updated eligibility_agent.py required documents extraction!")
