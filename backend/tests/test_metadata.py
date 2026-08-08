from app.rag.chunker import DocumentChunk
from app.rag.metadata import metadata_builder


def test_metadata_builder():
    """
    Test metadata generation for a single knowledge chunk.
    """

    chunk = DocumentChunk(
        text=(
            "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)\n"
            "4. Eligibility Criteria\n"
            "The farmer must satisfy the eligibility conditions."
        ),
        scheme_name=(
            "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)"
        ),
        section="Eligibility Criteria",
        domain="agriculture",
        chunk_id="agriculture_0004",
    )

    metadata = metadata_builder.build(
        chunk=chunk,
        source_file="Agriculture Schemes.docx",
    )

    assert metadata["scheme_name"] == (
        "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)"
    )

    assert metadata["section"] == "Eligibility Criteria"

    assert metadata["domain"] == "agriculture"

    assert metadata["source_file"] == (
        "Agriculture Schemes.docx"
    )

    assert metadata["source_type"] == "knowledge_base"

    print("\nGenerated metadata:")
    print(metadata)


def test_metadata_builder_for_multiple_chunks():
    """
    Test metadata generation for multiple chunks.
    """

    chunks = [
        DocumentChunk(
            text="PM-KISAN\n1. Scheme Overview",
            scheme_name=(
                "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)"
            ),
            section="Scheme Overview",
            domain="agriculture",
            chunk_id="agriculture_0001",
        ),
        DocumentChunk(
            text="PM-KISAN\n4. Eligibility Criteria",
            scheme_name=(
                "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)"
            ),
            section="Eligibility Criteria",
            domain="agriculture",
            chunk_id="agriculture_0004",
        ),
    ]

    metadata_list = metadata_builder.build_many(
        chunks=chunks,
        source_file="Agriculture Schemes.docx",
    )

    assert len(metadata_list) == 2

    assert metadata_list[0]["section"] == "Scheme Overview"
    assert metadata_list[1]["section"] == "Eligibility Criteria"

    assert metadata_list[0]["domain"] == "agriculture"
    assert metadata_list[1]["domain"] == "agriculture"

    assert (
        metadata_list[0]["source_file"]
        == "Agriculture Schemes.docx"
    )

    assert (
        metadata_list[1]["source_file"]
        == "Agriculture Schemes.docx"
    )

    print("\nGenerated metadata list:")

    for metadata in metadata_list:
        print(metadata)