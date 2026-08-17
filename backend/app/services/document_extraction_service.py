import json
import logging
import re
from typing import Any

from app.core.llm_json import parse_llm_json
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class DocumentExtractionService:
    """
    Extract structured citizen fields from OCR text of
    government identity and eligibility documents.
    """

    EXTRACTION_PROMPT = """
You extract structured citizen information from OCR text of
Indian government documents (Aadhaar, Voter ID, Ration Card,
Smart Ration Card, Birth Certificate, Land Record, Income
Certificate, Marksheet, Bank Passbook, Farmer ID, College ID etc.).

Return ONLY valid JSON in this exact format:

{
    "document_type": "aadhaar|voter_id|ration_card|smart_card|birth_certificate|land_record|income_certificate|marksheet|bank_passbook|farmer_id|enrollment_proof|college_id|other",
    "full_name": "",
    "date_of_birth": "",
    "age": null,
    "gender": "",
    "address": "",
    "state": "",
    "district": "",
    "pincode": "",
    "occupation": "",
    "is_farmer": null,
    "land_owner": null,
    "land_acres": "",
    "annual_income": "",
    "is_student": null,
    "course": "",
    "institution": "",
    "year_of_study": "",
    "institution_type": "",
    "bank_account_number": "",
    "aadhaar_number_last4": ""
}

Rules:
- Include ONLY fields clearly present in the text.
- Use null for unknown booleans and numbers.
- date_of_birth should be DD/MM/YYYY or YYYY-MM-DD when visible.
- document_type must reflect the most likely document.
- Do not invent values.
""".strip()

    def extract_from_text(
        self,
        ocr_text: str,
        filename: str = "",
    ) -> dict[str, Any]:
        if not ocr_text or not ocr_text.strip():
            return {
                "document_type": "other",
                "source_filename": filename,
            }

        user_prompt = f"""
FILENAME: {filename or "unknown"}

OCR TEXT:
{ocr_text.strip()}
""".strip()

        try:
            response = llm_service.generate(
                messages=[
                    {
                        "role": "system",
                        "content": self.EXTRACTION_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                temperature=0.0,
            )

            data = parse_llm_json(response)

            if not isinstance(data, dict):
                raise ValueError("Extraction did not return an object")

            data["source_filename"] = filename
            return self._normalize_fields(data)

        except Exception as exc:
            logger.warning(
                "Structured extraction failed for %s: %s",
                filename,
                exc,
            )
            return {
                "document_type": self._guess_document_type(
                    ocr_text,
                    filename,
                ),
                "source_filename": filename,
                "raw_ocr_available": True,
            }

    def _guess_document_type(
        self,
        ocr_text: str,
        filename: str,
    ) -> str:
        combined = f"{filename} {ocr_text}".lower()

        patterns = {
            "aadhaar": ["aadhaar", "aadhar", "uidai", "unique identification"],
            "voter_id": ["voter", "epic", "election commission"],
            "ration_card": ["ration card", "family card", "smart card"],
            "smart_card": ["smart card", "pds"],
            "birth_certificate": ["birth certificate", "date of birth"],
            "land_record": ["patta", "chitta", "land record", "land ownership"],
            "income_certificate": ["income certificate", "annual income"],
            "marksheet": ["marksheet", "mark sheet", "grade card"],
            "bank_passbook": ["passbook", "bank account", "ifsc"],
            "farmer_id": ["farmer", "pm-kisan", "kisan"],
            "enrollment_proof": ["enrollment", "admission"],
            "college_id": ["college id", "student id", "university id", "identity card"],
        }

        for doc_type, keywords in patterns.items():
            if any(keyword in combined for keyword in keywords):
                return doc_type

        return "other"

    def _normalize_fields(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        normalized: dict[str, Any] = {}

        for key, value in data.items():
            if value is None:
                continue

            if isinstance(value, str):
                value = value.strip()
                if not value:
                    continue

            normalized[key] = value

        doc_type = str(
            normalized.get(
                "document_type",
                "other",
            )
        ).strip().lower()

        normalized["document_type"] = doc_type or "other"

        age = normalized.get("age")
        if isinstance(age, str) and age.isdigit():
            normalized["age"] = int(age)

        return normalized

    def serialize_fields(
        self,
        fields: dict[str, Any],
    ) -> str:
        return json.dumps(fields)

    def deserialize_fields(
        self,
        raw: str | None,
    ) -> dict[str, Any]:
        if not raw:
            return {}

        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

        return {}


document_extraction_service = DocumentExtractionService()
