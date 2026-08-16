import re
from datetime import datetime
from typing import Any


class DocumentRequirementService:
    """
    Map eligibility information gaps to acceptable documents
    and determine when uploaded documents satisfy requirements.
    """

    REQUIREMENT_RULES: dict[str, dict[str, Any]] = {
        "age": {
            "patterns": [
                r"\bage\b",
                r"date of birth",
                r"\bdob\b",
                r"birth date",
                r"how old",
            ],
            "profile_keys": ["age", "date_of_birth"],
            "extracted_keys": ["age", "date_of_birth"],
            "documents": [
                "Age proof — Aadhaar, Voter ID, Birth Certificate, "
                "Passport, or School Certificate"
            ],
        },
        "residency": {
            "patterns": [
                r"\baddress\b",
                r"residen",
                r"domicile",
                r"\bstate\b",
                r"\bdistrict\b",
                r"location",
                r"tamil nadu",
            ],
            "profile_keys": [
                "address",
                "state",
                "district",
                "residency",
            ],
            "extracted_keys": [
                "address",
                "state",
                "district",
            ],
            "documents": [
                "Residency proof — Aadhaar, Voter ID, Ration Card, "
                "Smart Card, or Utility Bill"
            ],
        },
        "identity": {
            "patterns": [
                r"\bidentity\b",
                r"name proof",
                r"full name",
            ],
            "profile_keys": ["full_name", "name"],
            "extracted_keys": ["full_name"],
            "documents": [
                "Identity proof — Aadhaar, Voter ID, Passport, "
                "or PAN Card"
            ],
        },
        "land_ownership": {
            "patterns": [
                r"land owner",
                r"agricultural land",
                r"cultivat",
                r"land record",
                r"land details",
                r"land_acres",
            ],
            "profile_keys": [
                "land_owner",
                "land_acres",
                "land_details",
            ],
            "extracted_keys": [
                "land_owner",
                "land_acres",
            ],
            "documents": [
                "Land ownership proof — Patta/Chitta, Land Record, "
                "or Revenue Document"
            ],
        },
        "farmer_status": {
            "patterns": [
                r"\bfarmer\b",
                r"farming",
                r"cultivator",
            ],
            "profile_keys": [
                "occupation",
                "is_farmer",
            ],
            "extracted_keys": [
                "occupation",
                "is_farmer",
            ],
            "documents": [
                "Farmer status proof — Farmer ID, Land Record, "
                "or PM-KISAN enrollment proof"
            ],
        },
        "income": {
            "patterns": [
                r"\bincome\b",
                r"annual income",
                r"family income",
            ],
            "profile_keys": [
                "annual_income",
                "income",
            ],
            "extracted_keys": ["annual_income"],
            "documents": [
                "Income proof — Income Certificate or Salary Slip"
            ],
        },
        "student_status": {
            "patterns": [
                r"\bstudent\b",
                r"enrollment",
                r"currently studying",
                r"year of study",
                r"course",
                r"program",
                r"institution",
            ],
            "profile_keys": [
                "student",
                "student_status",
                "is_student",
                "course",
                "program",
                "year_of_study",
                "institution_type",
            ],
            "extracted_keys": [
                "is_student",
                "course",
                "institution",
                "year_of_study",
                "institution_type",
            ],
            "documents": [
                "Student proof — Marksheet, Bonafide Certificate, "
                "Admission Letter, or College ID Card"
            ],
        },
        "bank_account": {
            "patterns": [
                r"bank account",
                r"aadhaar.?seeded",
                r"dbt",
                r"passbook",
            ],
            "profile_keys": ["bank_account"],
            "extracted_keys": ["bank_account_number"],
            "documents": [
                "Bank account proof — Passbook or Bank Statement "
                "(Aadhaar-seeded)"
            ],
        },
        "gender": {
            "patterns": [r"\bgender\b", r"\bmale\b", r"\bfemale\b"],
            "profile_keys": ["gender"],
            "extracted_keys": ["gender"],
            "documents": [
                "Gender proof — Aadhaar, Voter ID, or Birth Certificate"
            ],
        },
    }

    DOCUMENT_SATISFIES: dict[str, set[str]] = {
        "aadhaar": {
            "age",
            "residency",
            "identity",
            "gender",
            "bank_account",
        },
        "voter_id": {
            "age",
            "residency",
            "identity",
            "gender",
        },
        "ration_card": {"residency", "identity"},
        "smart_card": {"residency", "identity"},
        "birth_certificate": {"age", "identity", "gender"},
        "land_record": {"land_ownership", "farmer_status"},
        "farmer_id": {"farmer_status", "land_ownership"},
        "income_certificate": {"income"},
        "marksheet": {"student_status", "identity"},
        "enrollment_proof": {"student_status"},
        "college_id": {"student_status", "identity"},
        "bank_passbook": {"bank_account", "identity"},
    }

    NO_DOCUMENT_PHRASES = [
        "don't have any documents",
        "do not have any documents",
        "don't have documents",
        "do not have documents",
        "no documents",
        "cannot upload",
        "can't upload",
        "dont have any documents",
        "dont have documents",
        "without documents",
        "i have no documents",
        "don't have any document",
        "do not have any document",
        "dont have those documents",
        "don't have those documents",
        "dont have them",
        "don't have them",
        "no document",
        "don't have",
        "dont have",
        "no proof",
    ]

    def user_declined_documents(
        self,
        query: str,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> bool:
        texts = [query.strip().lower()]

        if conversation_history:
            for message in conversation_history[-4:]:
                if message.get("role") == "user":
                    content = message.get("content", "").strip().lower()
                    if content:
                        texts.append(content)

        combined = " ".join(texts)

        return any(
            phrase in combined
            for phrase in self.NO_DOCUMENT_PHRASES
        )

    def classify_requirement(
        self,
        missing_item: str,
    ) -> str | None:
        text = missing_item.strip().lower()

        if not text:
            return None

        for requirement, rule in self.REQUIREMENT_RULES.items():
            for pattern in rule["patterns"]:
                if re.search(pattern, text):
                    return requirement

        return None

    def _has_value(
        self,
        profile: dict[str, Any],
        key: str,
    ) -> bool:
        value = profile.get(key)

        if value is None:
            return False

        if isinstance(value, str):
            return bool(value.strip())

        if isinstance(value, bool):
            return value

        return True

    def _compute_age_from_dob(
        self,
        dob: str,
    ) -> int | None:
        if not dob:
            return None

        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                birth = datetime.strptime(
                    dob.strip(),
                    fmt,
                )
                today = datetime.utcnow()
                age = (
                    today.year
                    - birth.year
                    - (
                        (today.month, today.day)
                        < (birth.month, birth.day)
                    )
                )
                return age
            except ValueError:
                continue

        return None

    def merge_extracted_into_profile(
        self,
        profile: dict[str, Any],
        extracted_documents: list[dict[str, Any]],
    ) -> dict[str, Any]:
        merged = dict(profile or {})

        for document in extracted_documents:
            fields = document.get("fields", document)

            if not isinstance(fields, dict):
                continue

            for key, value in fields.items():
                if key in {
                    "document_type",
                    "source_filename",
                    "raw_ocr_available",
                }:
                    continue

                if value is None:
                    continue

                if isinstance(value, str) and not value.strip():
                    continue

                merged[key] = value

            dob = fields.get("date_of_birth")
            if dob and not merged.get("age"):
                computed_age = self._compute_age_from_dob(dob)
                if computed_age is not None:
                    merged["age"] = computed_age

            doc_type = str(
                fields.get("document_type", "")
            ).lower()

            for requirement in self.DOCUMENT_SATISFIES.get(
                doc_type,
                set(),
            ):
                rule = self.REQUIREMENT_RULES.get(
                    requirement,
                    {},
                )

                for profile_key in rule.get(
                    "profile_keys",
                    [],
                ):
                    if self._has_value(fields, profile_key):
                        merged[profile_key] = fields[profile_key]

                for extracted_key in rule.get(
                    "extracted_keys",
                    [],
                ):
                    if self._has_value(fields, extracted_key):
                        merged[extracted_key] = fields[extracted_key]

        return merged

    def get_satisfied_requirements(
        self,
        profile: dict[str, Any],
        extracted_documents: list[dict[str, Any]],
    ) -> set[str]:
        satisfied: set[str] = set()
        merged_profile = self.merge_extracted_into_profile(
            profile,
            extracted_documents,
        )

        for requirement, rule in self.REQUIREMENT_RULES.items():
            if any(
                self._has_value(
                    merged_profile,
                    key,
                )
                for key in rule["profile_keys"]
            ):
                satisfied.add(requirement)

        for document in extracted_documents:
            fields = document.get(
                "fields",
                document,
            )

            if not isinstance(fields, dict):
                continue

            doc_type = str(
                fields.get("document_type", "other")
            ).lower()

            satisfied.update(
                self.DOCUMENT_SATISFIES.get(
                    doc_type,
                    set(),
                )
            )

            for requirement, rule in self.REQUIREMENT_RULES.items():
                if any(
                    self._has_value(fields, key)
                    for key in rule["extracted_keys"]
                ):
                    satisfied.add(requirement)

        return satisfied

    def filter_missing_information(
        self,
        missing_information: list[Any],
        profile: dict[str, Any],
        extracted_documents: list[dict[str, Any]],
    ) -> list[str]:
        satisfied = self.get_satisfied_requirements(
            profile,
            extracted_documents,
        )

        filtered: list[str] = []
        seen_requirements: set[str] = set()

        for item in missing_information:
            if not isinstance(item, str):
                continue

            item = item.strip()
            if not item:
                continue

            requirement = self.classify_requirement(item)

            if requirement and requirement in satisfied:
                continue

            if requirement:
                if requirement in seen_requirements:
                    continue
                seen_requirements.add(requirement)

            filtered.append(item)

        return filtered

    def build_required_documents(
        self,
        missing_information: list[Any],
    ) -> list[str]:
        documents: list[str] = []
        seen: set[str] = set()

        for item in missing_information:
            if not isinstance(item, str):
                continue

            requirement = self.classify_requirement(item)

            if not requirement:
                continue

            if requirement in seen:
                continue

            seen.add(requirement)
            rule = self.REQUIREMENT_RULES[requirement]
            documents.extend(rule["documents"])

        return documents

    def format_documents_for_prompt(
        self,
        documents: list[Any],
        extracted_documents: list[dict[str, Any]],
    ) -> str:
        sections: list[str] = []

        for index, document in enumerate(
            extracted_documents,
            start=1,
        ):
            fields = document.get("fields", {})

            if not isinstance(fields, dict):
                fields = {}

            filename = document.get(
                "filename",
                fields.get("source_filename", f"Document {index}"),
            )

            doc_type = document.get(
                "document_type",
                fields.get("document_type", "unknown"),
            )

            structured_lines = [
                f"DOCUMENT {index}: {filename}",
                f"Detected Type: {doc_type}",
            ]

            for key in [
                "full_name",
                "date_of_birth",
                "age",
                "gender",
                "address",
                "state",
                "district",
                "occupation",
                "land_owner",
                "land_acres",
                "annual_income",
                "is_student",
                "course",
                "institution",
                "year_of_study",
                "institution_type",
                "bank_account_number",
            ]:
                value = fields.get(key)
                if value is not None and value != "":
                    structured_lines.append(
                        f"{key}: {value}"
                    )

            ocr_text = ""
            if hasattr(document, "ocr_text"):
                ocr_text = document.ocr_text or ""
            elif isinstance(document, dict):
                ocr_text = document.get("ocr_text", "")

            if ocr_text:
                structured_lines.append(
                    f"Raw OCR excerpt: {ocr_text[:1200]}"
                )

            sections.append(
                "\n".join(structured_lines)
            )

        if not sections:
            return "(No documents provided)"

        return "\n\n".join(sections)


document_requirement_service = DocumentRequirementService()
