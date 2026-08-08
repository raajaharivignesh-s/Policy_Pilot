from app.rag.text_cleaner import text_cleaner


def test_text_cleaner():
    raw_text = """
        Scheme 1: PM-KISAN


        1. Scheme Overview

        Scheme Name     PM-KISAN


        2. Objective
    """

    cleaned = text_cleaner.clean(raw_text)

    assert cleaned
    assert "Scheme 1: PM-KISAN" in cleaned
    assert "1. Scheme Overview" in cleaned
    assert "2. Objective" in cleaned

    print("\nCleaned text:")
    print(cleaned)