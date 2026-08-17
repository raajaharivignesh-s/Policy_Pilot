import json
import re
from typing import Any


def parse_llm_json(response: str) -> dict[str, Any]:
    """
    Parse JSON returned by an LLM.

    Models sometimes wrap JSON in markdown code fences even
    when asked for raw JSON only.
    """

    text = (response or "").strip()

    if not text:
        raise json.JSONDecodeError(
            "Empty response",
            text,
            0,
        )

    if text.startswith("```"):
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(
            r"\s*```$",
            "",
            text,
        ).strip()

    return json.loads(text)
