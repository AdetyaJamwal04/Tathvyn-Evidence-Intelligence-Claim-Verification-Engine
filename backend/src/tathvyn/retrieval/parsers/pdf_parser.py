"""PDF Document Extractor using PyPDF.

Extracts text content and metadata from PDF byte payloads with size and page caps.
"""

import io
from typing import NamedTuple

from pypdf import PdfReader

from tathvyn.common.logging import get_logger

logger = get_logger("pdf_parser")


class ParsedPDFResult(NamedTuple):
    """Result of PDF text extraction."""

    main_text: str
    title: str | None
    author: str | None
    page_count: int


def parse_pdf_content(pdf_bytes: bytes, max_pages: int = 50) -> ParsedPDFResult:
    """Extract text from raw PDF bytes up to max_pages limit.

    Args:
        pdf_bytes: Raw bytes of the PDF file.
        max_pages: Maximum pages to parse to prevent memory bloat.

    Returns:
        ParsedPDFResult: Concatenated text, metadata title, author, and page count.
    """
    if not pdf_bytes:
        return ParsedPDFResult(main_text="", title=None, author=None, page_count=0)

    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        total_pages = len(reader.pages)
        pages_to_read = min(total_pages, max_pages)

        extracted_chunks: list[str] = []
        for idx in range(pages_to_read):
            page = reader.pages[idx]
            page_text = page.extract_text() or ""
            if page_text.strip():
                extracted_chunks.append(page_text.strip())

        full_text = "\n\n".join(extracted_chunks)

        meta = reader.metadata
        title = meta.title if meta and meta.title else None
        author = meta.author if meta and meta.author else None

        return ParsedPDFResult(
            main_text=full_text,
            title=title,
            author=author,
            page_count=total_pages,
        )
    except Exception as e:
        logger.warning("Failed to extract text from PDF payload", error=str(e))
        return ParsedPDFResult(main_text="", title=None, author=None, page_count=0)
