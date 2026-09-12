"""HTML Content Extractor using Trafilatura.

Extracts article main text, title, author, and publication date from raw HTML,
stripping navigation menus, advertisements, and boilerplate.
"""

from typing import NamedTuple

import trafilatura
from trafilatura.settings import use_config

from tathvyn.common.logging import get_logger

logger = get_logger("html_parser")

# Fast trafilatura config
_TRAFILATURA_CONFIG = use_config()
_TRAFILATURA_CONFIG.set("DEFAULT", "EXTRACTION_TIMEOUT", "5")


class ParsedHTMLResult(NamedTuple):
    """Result of HTML extraction."""

    main_text: str
    title: str | None
    author: str | None
    published_date: str | None


def parse_html_content(raw_html: str, url: str | None = None) -> ParsedHTMLResult:
    """Extract clean main text and metadata from raw HTML bytes/string.

    Args:
        raw_html: Raw HTML string.
        url: Optional document URL for relative link resolution.

    Returns:
        ParsedHTMLResult: Clean main text, title, author, and date.
    """
    if not raw_html or len(raw_html.strip()) == 0:
        return ParsedHTMLResult(main_text="", title=None, author=None, published_date=None)

    extracted_text = trafilatura.extract(
        raw_html,
        url=url,
        config=_TRAFILATURA_CONFIG,
        include_comments=False,
        include_tables=True,
        output_format="txt",
        no_fallback=False,
    )

    metadata = trafilatura.extract_metadata(raw_html, default_url=url)
    title = metadata.title if metadata else None
    author = metadata.author if metadata else None
    date_str = metadata.date if metadata else None

    main_text = extracted_text if extracted_text else ""

    return ParsedHTMLResult(
        main_text=main_text,
        title=title,
        author=author,
        published_date=date_str,
    )
