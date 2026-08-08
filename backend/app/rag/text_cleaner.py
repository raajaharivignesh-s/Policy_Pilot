import re


class TextCleaner:
    """
    Cleans extracted knowledge-base text while preserving
    meaningful headings, sections, and content.
    """

    def clean(self, text: str) -> str:
        if not text:
            return ""

        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Remove excessive spaces/tabs
        text = re.sub(r"[ \t]+", " ", text)

        # Remove excessive blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Remove spaces around line boundaries
        lines = [
            line.strip()
            for line in text.split("\n")
        ]

        # Remove empty lines at beginning/end
        while lines and not lines[0]:
            lines.pop(0)

        while lines and not lines[-1]:
            lines.pop()

        return "\n".join(lines)


text_cleaner = TextCleaner()