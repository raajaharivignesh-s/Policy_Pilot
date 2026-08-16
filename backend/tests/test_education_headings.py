from pathlib import Path

from app.rag.document_loader import document_loader
from app.rag.text_cleaner import text_cleaner


PROJECT_ROOT = Path(__file__).resolve().parents[2]

FILE_PATH = (
    PROJECT_ROOT
    / "knowledge_base"
    / "raw"
    / "education"
    / "Education Schemes.docx"
)


def test_education_headings():

    loaded = document_loader.load(FILE_PATH)

    cleaned_text = text_cleaner.clean(
        loaded["text"]
    )

    lines = cleaned_text.splitlines()

    targets = [
        "TAMIZH",
        "MINORITY",
    ]

    for index, line in enumerate(lines):

        if any(
            target in line.upper()
            for target in targets
        ):

            print("\n" + "=" * 70)

            start = max(0, index - 3)
            end = min(
                len(lines),
                index + 4,
            )

            for line_number in range(
                start,
                end,
            ):

                print(
                    f"{line_number:04d}: "
                    f"{lines[line_number]!r}"
                )

            print("=" * 70)