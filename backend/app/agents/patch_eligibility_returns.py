import re

with open('eligibility_agent.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update the first return (intent check)
old_1 = """        if intent != "eligibility_check":

            return {
                "eligibility_results": [],
            }"""

new_1 = """        if intent != "eligibility_check":

            return {
                "eligibility_results": [],
                "required_documents": [],
            }"""

content = content.replace(old_1, new_1)

# 2. Update the supported_information return
old_2 = """            return {
                "eligibility_results": [
                    {
                        "scheme_name": scheme_name,
                        "status": (
                            "insufficient_information"
                        ),
                        "matched_rules": [],
                        "failed_rules": [],
                        "missing_information": (
                            missing_information
                        ),
                        "reason": (
                            "Eligibility cannot be confirmed "
                            "because sufficiently verified "
                            "scheme-specific eligibility "
                            "information is not available."
                        ),
                    }
                ],
            }"""

new_2 = """            return {
                "eligibility_results": [
                    {
                        "scheme_name": scheme_name,
                        "status": (
                            "insufficient_information"
                        ),
                        "matched_rules": [],
                        "failed_rules": [],
                        "missing_information": (
                            missing_information
                        ),
                        "reason": (
                            "Eligibility cannot be confirmed "
                            "because sufficiently verified "
                            "scheme-specific eligibility "
                            "information is not available."
                        ),
                    }
                ],
                "required_documents": [],
            }"""

content = content.replace(old_2, new_2)

# 3. Update the evidence_parts check return
old_3 = """            return {
                "eligibility_results": [
                    {
                        "scheme_name": scheme_name,
                        "status": (
                            "insufficient_information"
                        ),
                        "matched_rules": [],
                        "failed_rules": [],
                        "missing_information": (
                            missing_information
                        ),
                        "reason": (
                            "The available verified information "
                            "does not contain explicit eligibility "
                            "criteria sufficient to determine "
                            "eligibility."
                        ),
                    }
                ],
            }"""

new_3 = """            return {
                "eligibility_results": [
                    {
                        "scheme_name": scheme_name,
                        "status": (
                            "insufficient_information"
                        ),
                        "matched_rules": [],
                        "failed_rules": [],
                        "missing_information": (
                            missing_information
                        ),
                        "reason": (
                            "The available verified information "
                            "does not contain explicit eligibility "
                            "criteria sufficient to determine "
                            "eligibility."
                        ),
                    }
                ],
                "required_documents": [],
            }"""

content = content.replace(old_3, new_3)

# 4. Update JSON Decode Error return
old_4 = """            return {
                "eligibility_results": [
                    {
                        "scheme_name": scheme_name,
                        "status": (
                            "insufficient_information"
                        ),
                        "matched_rules": [],
                        "failed_rules": [],
                        "missing_information": [
                            (
                                "Additional information "
                                "required to evaluate eligibility"
                            )
                        ],
                        "reason": (
                            "Eligibility could not be "
                            "determined from the verified "
                            "evidence."
                        ),
                    }
                ],
                "errors": [
                    "Eligibility Agent returned invalid JSON."
                ],
            }"""

new_4 = """            return {
                "eligibility_results": [
                    {
                        "scheme_name": scheme_name,
                        "status": (
                            "insufficient_information"
                        ),
                        "matched_rules": [],
                        "failed_rules": [],
                        "missing_information": [
                            (
                                "Additional information "
                                "required to evaluate eligibility"
                            )
                        ],
                        "reason": (
                            "Eligibility could not be "
                            "determined from the verified "
                            "evidence."
                        ),
                    }
                ],
                "required_documents": [],
                "errors": [
                    "Eligibility Agent returned invalid JSON."
                ],
            }"""

content = content.replace(old_4, new_4)

# 5. Update validated_results fallback return
old_5 = """        if not validated_results:

            return {
                "eligibility_results": [
                    {
                        "scheme_name": scheme_name,
                        "status": (
                            "insufficient_information"
                        ),
                        "matched_rules": [],
                        "failed_rules": [],
                        "missing_information": [
                            (
                                "Additional information "
                                "required to evaluate eligibility"
                            )
                        ],
                        "reason": (
                            "Eligibility could not be "
                            "determined from the supplied "
                            "verified evidence."
                        ),
                    }
                ],
            }"""

new_5 = """        if not validated_results:

            return {
                "eligibility_results": [
                    {
                        "scheme_name": scheme_name,
                        "status": (
                            "insufficient_information"
                        ),
                        "matched_rules": [],
                        "failed_rules": [],
                        "missing_information": [
                            (
                                "Additional information "
                                "required to evaluate eligibility"
                            )
                        ],
                        "reason": (
                            "Eligibility could not be "
                            "determined from the supplied "
                            "verified evidence."
                        ),
                    }
                ],
                "required_documents": [],
            }"""

content = content.replace(old_5, new_5)

with open('eligibility_agent.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Patched all returns in eligibility_agent.py!")
