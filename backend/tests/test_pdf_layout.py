"""
Tests for PDF layout extraction (utils/pdf_layout).

Uses PyMuPDF (fitz) to create PDFs in memory for deterministic testing.
"""

import sys
from pathlib import Path

# Ensure the backend src directory is on the import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import fitz  # PyMuPDF
import pytest

from utils.pdf_layout import (
    BlockType,
    DocumentLayout,
    LayoutBlock,
    _compute_modal_font_size,
    _is_list_item,
    extract_layout,
)


# ── Helpers ───────────────────────────────────────────────────────────


def _make_pdf(pages: list[list[tuple[str, float, tuple[float, float]]]]) -> bytes:
    """Create a minimal PDF in memory.

    Args:
        pages: list of pages, where each page is a list of
               (text, font_size, (x, y)) tuples.

    Returns:
        PDF file bytes.
    """
    doc = fitz.open()
    for page_items in pages:
        page = doc.new_page(width=612, height=792)  # US Letter
        for text, font_size, (x, y) in page_items:
            page.insert_text(
                fitz.Point(x, y),
                text,
                fontsize=font_size,
                fontname="helv",
            )
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def simple_pdf() -> bytes:
    """A one-page PDF with a heading and two body paragraphs."""
    return _make_pdf(
        [
            [
                ("My Big Heading", 24.0, (72, 80)),
                ("This is body paragraph one.", 12.0, (72, 140)),
                ("This is body paragraph two.", 12.0, (72, 200)),
            ]
        ]
    )


@pytest.fixture
def list_pdf() -> bytes:
    """A one-page PDF containing list items."""
    return _make_pdf(
        [
            [
                ("- First bullet item", 12.0, (72, 80)),
                ("* Second bullet item", 12.0, (72, 110)),
                ("1. Numbered item", 12.0, (72, 140)),
            ]
        ]
    )


@pytest.fixture
def multi_page_pdf() -> bytes:
    """A two-page PDF."""
    return _make_pdf(
        [
            [
                ("Page one text", 12.0, (72, 80)),
            ],
            [
                ("Page two text", 12.0, (72, 80)),
            ],
        ]
    )


@pytest.fixture
def empty_pdf() -> bytes:
    """A PDF with no text at all."""
    doc = fitz.open()
    doc.new_page()
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


# ── Tests for _is_list_item ───────────────────────────────────────────


class TestIsListItem:
    def test_dash_prefix(self):
        assert _is_list_item("- buy milk") is True

    def test_asterisk_prefix(self):
        assert _is_list_item("* buy milk") is True

    def test_bullet_prefix(self):
        assert _is_list_item("• buy milk") is True

    def test_numbered_dot(self):
        assert _is_list_item("1. First item") is True

    def test_numbered_paren(self):
        assert _is_list_item("2) Second item") is True

    def test_multi_digit_numbered(self):
        assert _is_list_item("12. Twelfth item") is True

    def test_leading_whitespace(self):
        assert _is_list_item("   - indented bullet") is True

    def test_plain_text_not_list(self):
        assert _is_list_item("Hello world") is False

    def test_dash_without_space(self):
        assert _is_list_item("-no space") is False

    def test_number_without_marker(self):
        assert _is_list_item("123 not a list") is False

    def test_empty_string(self):
        assert _is_list_item("") is False


# ── Tests for _compute_modal_font_size ────────────────────────────────


class TestComputeModalFontSize:
    def test_picks_most_common_size(self):
        raw_blocks = [
            {
                "lines": [
                    {
                        "spans": [
                            {"text": "heading", "size": 24.0},
                        ]
                    },
                    {
                        "spans": [
                            {"text": "body text that is much longer than the heading text above", "size": 12.0},
                        ]
                    },
                ]
            }
        ]
        assert _compute_modal_font_size(raw_blocks) == 12.0

    def test_empty_blocks_returns_default(self):
        assert _compute_modal_font_size([]) == 12.0

    def test_whitespace_only_spans_ignored(self):
        raw_blocks = [
            {
                "lines": [
                    {
                        "spans": [
                            {"text": "   ", "size": 99.0},
                            {"text": "real text", "size": 11.0},
                        ]
                    }
                ]
            }
        ]
        assert _compute_modal_font_size(raw_blocks) == 11.0

    def test_multiple_sizes_picks_highest_char_count(self):
        """When two sizes compete, the one with more total chars wins."""
        raw_blocks = [
            {
                "lines": [
                    {
                        "spans": [
                            {"text": "short", "size": 18.0},
                            {
                                "text": "this is a significantly longer body of text",
                                "size": 10.0,
                            },
                        ]
                    }
                ]
            }
        ]
        assert _compute_modal_font_size(raw_blocks) == 10.0


# ── Tests for extract_layout ──────────────────────────────────────────


class TestExtractLayout:
    def test_returns_document_layout(self, simple_pdf: bytes):
        result = extract_layout(simple_pdf)
        assert isinstance(result, DocumentLayout)

    def test_heading_detected(self, simple_pdf: bytes):
        result = extract_layout(simple_pdf)
        headings = [b for b in result.blocks if b.block_type == BlockType.HEADING]
        assert len(headings) >= 1
        assert "My Big Heading" in headings[0].text

    def test_paragraph_detected(self, simple_pdf: bytes):
        result = extract_layout(simple_pdf)
        paragraphs = [b for b in result.blocks if b.block_type == BlockType.PARAGRAPH]
        assert len(paragraphs) >= 1

    def test_heading_has_positive_heading_level(self, simple_pdf: bytes):
        result = extract_layout(simple_pdf)
        headings = [b for b in result.blocks if b.block_type == BlockType.HEADING]
        assert len(headings) >= 1
        assert headings[0].heading_level > 0

    def test_paragraph_has_zero_heading_level(self, simple_pdf: bytes):
        result = extract_layout(simple_pdf)
        paragraphs = [b for b in result.blocks if b.block_type == BlockType.PARAGRAPH]
        for p in paragraphs:
            assert p.heading_level == 0

    def test_list_items_detected(self, list_pdf: bytes):
        result = extract_layout(list_pdf)
        list_items = [b for b in result.blocks if b.block_type == BlockType.LIST_ITEM]
        assert len(list_items) >= 2

    def test_page_numbers_correct(self, multi_page_pdf: bytes):
        result = extract_layout(multi_page_pdf)
        assert result.page_count == 2
        page_numbers = {b.page_number for b in result.blocks}
        assert 1 in page_numbers
        assert 2 in page_numbers

    def test_empty_pdf_returns_empty_blocks(self, empty_pdf: bytes):
        result = extract_layout(empty_pdf)
        assert result.blocks == []
        assert result.page_count == 1

    def test_blocks_have_bboxes(self, simple_pdf: bytes):
        result = extract_layout(simple_pdf)
        for block in result.blocks:
            assert len(block.bbox) == 4
            x0, y0, x1, y1 = block.bbox
            assert x1 > x0
            assert y1 > y0

    def test_blocks_have_spans(self, simple_pdf: bytes):
        result = extract_layout(simple_pdf)
        for block in result.blocks:
            assert len(block.spans) >= 1
            for span in block.spans:
                assert span.text.strip() != ""
                assert span.font_size > 0

    def test_large_font_is_heading_small_font_is_paragraph(self):
        """Directly verify the font-size heuristic."""
        pdf_bytes = _make_pdf(
            [
                [
                    # Large font text — should be a heading
                    ("Title Text", 28.0, (72, 80)),
                    # Normal font text — should be a paragraph
                    ("Normal body text that has enough chars to be modal.", 11.0, (72, 150)),
                    ("More normal text for extra weight in modal calculation.", 11.0, (72, 200)),
                ]
            ]
        )
        result = extract_layout(pdf_bytes)
        headings = [b for b in result.blocks if b.block_type == BlockType.HEADING]
        paragraphs = [b for b in result.blocks if b.block_type == BlockType.PARAGRAPH]
        assert len(headings) >= 1
        assert "Title Text" in headings[0].text
        assert len(paragraphs) >= 1
