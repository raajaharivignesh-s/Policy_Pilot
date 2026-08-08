from app.rag.chunker import scheme_chunker


def test_scheme_chunker():
    text = """
    Scheme 1: PM-KISAN

    1. Scheme Overview
    PM-KISAN provides financial assistance to eligible farmer families.

    2. Objective
    The scheme supports agricultural activities and household needs.

    3. Benefits
    Eligible farmers receive financial assistance.

    4. Eligibility Criteria
    The farmer must satisfy the scheme eligibility conditions.

    6. Required Documents
    Aadhaar Card, bank passbook and land documents.

    7. Application Process
    Apply through the official portal or authorized center.

    Scheme 2: PMFBY

    1. Scheme Overview
    PMFBY provides crop insurance.

    4. Eligibility Criteria
    Farmers cultivating notified crops may be eligible.
    """

    chunks = scheme_chunker.chunk(
        text=text,
        domain="agriculture",
    )

    assert chunks

    assert len(chunks) == 8

    assert chunks[0].scheme_name == "PM-KISAN"
    assert chunks[0].section == "Scheme Overview"

    assert chunks[1].scheme_name == "PM-KISAN"
    assert chunks[1].section == "Objective"

    assert chunks[2].section == "Benefits"

    assert chunks[3].section == "Eligibility Criteria"

    assert chunks[4].section == "Required Documents"

    assert chunks[5].section == "Application Process"

    assert chunks[6].scheme_name == "PMFBY"
    assert chunks[6].section == "Scheme Overview"

    assert chunks[7].scheme_name == "PMFBY"
    assert chunks[7].section == "Eligibility Criteria"

    for chunk in chunks:
        assert chunk.domain == "agriculture"
        assert chunk.text
        assert chunk.chunk_id

    print("\nGenerated chunks:")

    for chunk in chunks:
        print("\n------------------------")
        print("Chunk ID:", chunk.chunk_id)
        print("Scheme:", chunk.scheme_name)
        print("Section:", chunk.section)
        print("Domain:", chunk.domain)
        print("Text:")
        print(chunk.text)