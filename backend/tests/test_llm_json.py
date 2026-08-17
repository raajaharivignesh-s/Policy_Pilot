import json

import pytest

from app.core.llm_json import parse_llm_json


def test_parse_llm_json_plain_object():
    data = parse_llm_json('{"verified_information": []}')
    assert data == {"verified_information": []}


def test_parse_llm_json_markdown_fence():
    response = """```json
{
    "verified_information": [
        {
            "document_index": 1,
            "supported": true
        }
    ]
}
```"""

    data = parse_llm_json(response)

    assert len(data["verified_information"]) == 1
    assert data["verified_information"][0]["supported"] is True


def test_parse_llm_json_empty_response():
    with pytest.raises(json.JSONDecodeError):
        parse_llm_json("")
