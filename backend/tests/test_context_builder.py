from app.rag.context_builder import context_builder
from app.rag.retriever import RetrievedDocument


def test_context_builder():

    documents = [
        RetrievedDocument(
            text=(
                "Eligible farmers receive financial "
                "assistance under the scheme."
            ),
            metadata={
                "scheme_name": "PM-KISAN",
                "section": "Benefits",
                "domain": "agriculture",
                "source_file": "Agriculture Schemes.docx",
            },
            distance=0.9,
        ),
        RetrievedDocument(
            text=(
                "Farmers must satisfy the eligibility "
                "conditions."
            ),
            metadata={
                "scheme_name": "PM-KISAN",
                "section": "Eligibility Criteria",
                "domain": "agriculture",
                "source_file": "Agriculture Schemes.docx",
            },
            distance=0.95,
        ),
    ]

    result = context_builder.build(documents)

    print("\n========================================")
    print("Generated RAG Context")
    print("========================================")
    print(result.context)

    assert result.context

    assert "PM-KISAN" in result.context

    assert "Benefits" in result.context

    assert "Eligibility Criteria" in result.context

    assert "Agriculture Schemes.docx" in result.context

    assert len(result.documents) == 2


def test_empty_context():

    result = context_builder.build([])

    assert result.context == ""

    assert result.documents == []