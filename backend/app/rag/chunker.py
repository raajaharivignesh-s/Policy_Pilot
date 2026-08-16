import re
from dataclasses import dataclass


@dataclass
class DocumentChunk:
    """
    Represents one logical chunk of knowledge.
    """

    text: str
    scheme_name: str
    section: str
    domain: str
    chunk_id: str


class SchemeChunker:
    """
    Splits PolicyPilot knowledge documents into
    scheme-aware and section-aware chunks.

    Supports multiple source-document formats, including:

    1. Scheme 1: PM-KISAN
    2. PUDHUMAI PENN SCHEME
    3. TAMIZH PUDHALVAN SCHEME — Knowledge Base Entry
    4. SCHOLARSHIP FOR DIFFERENTLY ABLED STUDENTS
    5. MINORITY POST-MATRIC SCHOLARSHIP — Knowledge Base Entry
    """

    NUMBERED_SCHEME_PATTERN = re.compile(
        r"^Scheme\s+\d+\s*:\s*(.+)$",
        re.IGNORECASE,
    )

    SECTION_PATTERN = re.compile(
        r"^(\d+)\.\s+(.+)$"
    )

    KNOWLEDGE_BASE_SUFFIX_PATTERN = re.compile(
        r"\s*[—–-]\s*Knowledge\s+Base\s+Entry\s*$",
        re.IGNORECASE,
    )

    def _normalize_named_scheme_heading(
        self,
        line: str,
    ) -> str:
        """
        Normalize named scheme headings.

        Example:

            TAMIZH PUDHALVAN SCHEME — Knowledge Base Entry

        becomes:

            TAMIZH PUDHALVAN SCHEME
        """

        stripped = line.strip()

        normalized = self.KNOWLEDGE_BASE_SUFFIX_PATTERN.sub(
            "",
            stripped,
        ).strip()

        return normalized

    def _is_named_scheme_heading(
        self,
        line: str,
    ) -> bool:
        """
        Detect scheme headings that are written as standalone
        uppercase titles.

        Supports headings such as:

            PUDHUMAI PENN SCHEME

        and:

            TAMIZH PUDHALVAN SCHEME — Knowledge Base Entry

            MINORITY POST-MATRIC SCHOLARSHIP — Knowledge Base Entry
        """

        stripped = line.strip()

        if not stripped:
            return False

        # Avoid treating generic document titles as schemes.
        excluded_titles = {
            "EDUCATION",
            "AGRICULTURE",
            "HEALTHCARE",
            "HEALTH CARE",
        }

        if stripped.upper() in excluded_titles:
            return False

        # Remove the standard knowledge-base suffix before
        # checking the actual scheme heading.
        heading = self._normalize_named_scheme_heading(
            stripped
        )

        if not heading:
            return False

        # Named scheme headings are expected to be uppercase.
        if heading != heading.upper():
            return False

        scheme_keywords = (
            "SCHEME",
            "SCHOLARSHIP",
            "PROGRAMME",
            "PROGRAM",
        )

        return any(
            keyword in heading
            for keyword in scheme_keywords
        )

    def chunk(
        self,
        text: str,
        domain: str,
    ) -> list[DocumentChunk]:
        """
        Split cleaned text into logical scheme/section chunks.
        """

        if not text.strip():
            return []

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        chunks: list[DocumentChunk] = []

        current_scheme = ""
        current_section = ""
        current_content: list[str] = []

        chunk_number = 0

        def save_chunk() -> None:
            nonlocal chunk_number

            # A section is required before creating a chunk.
            if not current_scheme:
                return

            if not current_section:
                return

            if not current_content:
                return

            content = "\n".join(
                current_content
            ).strip()

            if not content:
                return

            chunk_number += 1

            chunks.append(
                DocumentChunk(
                    text=content,
                    scheme_name=current_scheme,
                    section=current_section,
                    domain=domain,
                    chunk_id=(
                        f"{domain}_{chunk_number:04d}"
                    ),
                )
            )

        for line in lines:

            # --------------------------------------------------
            # Format 1:
            # Scheme 1: PM-KISAN
            # --------------------------------------------------

            numbered_scheme_match = (
                self.NUMBERED_SCHEME_PATTERN.match(
                    line
                )
            )

            if numbered_scheme_match:

                save_chunk()

                current_scheme = (
                    numbered_scheme_match
                    .group(1)
                    .strip()
                )

                current_section = ""
                current_content = []

                continue

            # --------------------------------------------------
            # Format 2:
            #
            # PUDHUMAI PENN SCHEME
            #
            # TAMIZH PUDHALVAN SCHEME
            # — Knowledge Base Entry
            #
            # MINORITY POST-MATRIC SCHOLARSHIP
            # — Knowledge Base Entry
            # --------------------------------------------------

            if self._is_named_scheme_heading(line):

                save_chunk()

                current_scheme = (
                    self._normalize_named_scheme_heading(
                        line
                    )
                )

                current_section = ""
                current_content = []

                continue

            # --------------------------------------------------
            # Numbered sections:
            #
            # 1. Scheme Overview
            # 2. Objective
            # 3. Benefits
            # 4. Eligibility
            # --------------------------------------------------

            section_match = self.SECTION_PATTERN.match(
                line
            )

            if section_match and current_scheme:

                save_chunk()

                section_number = (
                    section_match.group(1)
                )

                section_name = (
                    section_match.group(2).strip()
                )

                current_section = section_name

                current_content = [
                    current_scheme,
                    (
                        f"{section_number}. "
                        f"{section_name}"
                    ),
                ]

                continue

            # --------------------------------------------------
            # Normal content
            # --------------------------------------------------

            if current_scheme and current_section:
                current_content.append(line)

        # Save final section.
        save_chunk()

        return chunks


scheme_chunker = SchemeChunker()