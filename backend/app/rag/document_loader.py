from pathlib import Path
from typing import Any

from docx import Document
from docx.document import Document as DocumentObject
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P


class DocumentLoader:
    """
    Loads PolicyPilot DOCX knowledge documents.

    The loader preserves the original order of paragraphs
    and tables so that structured table information remains
    associated with the correct section of the document.
    """

    SUPPORTED_EXTENSIONS = {".docx"}

    def load(self, file_path: str | Path) -> dict[str, Any]:
        """
        Load a DOCX file and extract paragraphs and tables
        while preserving their original document order.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Knowledge document not found: {path}"
            )

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported document type: {path.suffix}"
            )

        document = Document(path)

        paragraphs: list[str] = []
        tables: list[list[list[str]]] = []
        ordered_content: list[str] = []

        # --------------------------------------------------
        # Walk through the document in its original order
        # --------------------------------------------------
        for element in self._iter_block_items(document):

            if isinstance(element, Paragraph):

                text = element.text.strip()

                if text:
                    paragraphs.append(text)
                    ordered_content.append(text)

            elif isinstance(element, Table):

                table_rows: list[list[str]] = []

                for row in element.rows:

                    cells = [
                        cell.text.strip()
                        for cell in row.cells
                    ]

                    if any(cells):
                        table_rows.append(cells)

                if not table_rows:
                    continue

                tables.append(table_rows)

                # Convert the table into readable text.
                # Each row becomes one line.
                for row in table_rows:

                    row_text = " | ".join(
                        cell for cell in row if cell
                    )

                    if row_text:
                        ordered_content.append(row_text)

        unified_text = "\n".join(ordered_content)

        return {
            "file_name": path.name,
            "file_path": str(path),
            "extension": path.suffix.lower(),
            "paragraphs": paragraphs,
            "tables": tables,
            "text": unified_text,
        }

    @staticmethod
    def _iter_block_items(
        parent: DocumentObject,
    ):
        """
        Yield paragraphs and tables in the exact order
        in which they appear in the DOCX document.
        """

        parent_element = parent.element.body

        for child in parent_element.iterchildren():

            if isinstance(child, CT_P):
                yield Paragraph(child, parent)

            elif isinstance(child, CT_Tbl):
                yield Table(child, parent)


document_loader = DocumentLoader()