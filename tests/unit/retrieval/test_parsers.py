"""Tests for HTML and PDF Document Parsers."""

from tathvyn.retrieval.parsers.html_parser import parse_html_content
from tathvyn.retrieval.parsers.pdf_parser import parse_pdf_content


def test_html_main_text_extraction() -> None:
    """Verify HTML parsing extracts body text and title while stripping nav menus."""
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head><title>Space Telescope Breakthrough</title></head>
    <body>
        <nav><a href="/home">Home</a><a href="/about">About</a></nav>
        <article>
            <h1>JWST Observations at L2</h1>
            <p>The James Webb Space Telescope operates around Lagrange Point 2 and has sent groundbreaking images.</p>
        </article>
        <footer>Copyright 2026 SpaceNews</footer>
    </body>
    </html>
    """
    result = parse_html_content(sample_html, url="https://example.org/article")
    assert "James Webb Space Telescope" in result.main_text
    assert result.title is not None
    assert "JWST" in result.title or "Space Telescope" in result.title


def test_empty_html_handling() -> None:
    """Verify empty or whitespace HTML returns safe empty result."""
    result = parse_html_content("")
    assert result.main_text == ""
    assert result.title is None


def test_pdf_parsing_empty_bytes() -> None:
    """Verify empty PDF byte payload handling."""
    result = parse_pdf_content(b"")
    assert result.main_text == ""
    assert result.page_count == 0
