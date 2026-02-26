"""
Tests for format renderers (utils/format_renderers).

Verifies that LayoutBlocks are correctly rendered to plaintext,
Markdown (GFM), and LaTeX output.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from utils.format_renderers import (
    _escape_latex,
    _group_table_cells,
    render_latex,
    render_markdown,
    render_plaintext,
)
from utils.pdf_layout import BlockType, LayoutBlock, TextSpan


# ── Helpers ───────────────────────────────────────────────────────────


def _block(
    block_type: BlockType,
    text: str,
    heading_level: int = 0,
    indent_level: int = 0,
    page_number: int = 1,
    bbox: tuple[float, float, float, float] = (72.0, 100.0, 500.0, 120.0),
    spans: list[TextSpan] | None = None,
) -> LayoutBlock:
    """Convenience factory for LayoutBlock instances."""
    if spans is None:
        spans = [
            TextSpan(
                text=text,
                font_name="Helvetica",
                font_size=12.0,
                is_bold=False,
                is_italic=False,
            )
        ]
    return LayoutBlock(
        block_type=block_type,
        text=text,
        spans=spans,
        bbox=bbox,
        page_number=page_number,
        heading_level=heading_level,
        indent_level=indent_level,
    )


def _table_cell(
    text: str,
    y: float,
    x: float,
    page_number: int = 1,
) -> LayoutBlock:
    """Create a TABLE_CELL block at a given (x, y) position."""
    return _block(
        BlockType.TABLE_CELL,
        text,
        page_number=page_number,
        bbox=(x, y, x + 100.0, y + 15.0),
    )


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def heading1() -> LayoutBlock:
    return _block(BlockType.HEADING, "Introduction", heading_level=1)


@pytest.fixture
def heading2() -> LayoutBlock:
    return _block(BlockType.HEADING, "Background", heading_level=2)


@pytest.fixture
def heading3() -> LayoutBlock:
    return _block(BlockType.HEADING, "Details", heading_level=3)


@pytest.fixture
def paragraph() -> LayoutBlock:
    return _block(BlockType.PARAGRAPH, "Some body text here.")


@pytest.fixture
def list_item() -> LayoutBlock:
    return _block(BlockType.LIST_ITEM, "- First bullet", indent_level=0)


@pytest.fixture
def bold_paragraph() -> LayoutBlock:
    return _block(
        BlockType.PARAGRAPH,
        "Bold text",
        spans=[
            TextSpan(
                text="Bold text",
                font_name="Helvetica-Bold",
                font_size=12.0,
                is_bold=True,
                is_italic=False,
            )
        ],
    )


@pytest.fixture
def table_blocks() -> list[LayoutBlock]:
    """A 2-row, 3-column table (cells at the same y are one row)."""
    y_row1 = 200.0
    y_row2 = 220.0
    return [
        _table_cell("Name", y_row1, 72.0),
        _table_cell("Age", y_row1, 200.0),
        _table_cell("City", y_row1, 330.0),
        _table_cell("Alice", y_row2, 72.0),
        _table_cell("30", y_row2, 200.0),
        _table_cell("NYC", y_row2, 330.0),
    ]


# ── Plaintext renderer ───────────────────────────────────────────────


class TestRenderPlaintext:
    def test_empty_blocks(self):
        assert render_plaintext([]) == "\n"

    def test_heading_level1_uppercase_underline(self, heading1: LayoutBlock):
        output = render_plaintext([heading1])
        assert "INTRODUCTION" in output
        assert "=" * len("Introduction") in output

    def test_heading_level2_underline(self, heading2: LayoutBlock):
        output = render_plaintext([heading2])
        assert "Background" in output
        assert "-" * len("Background") in output

    def test_heading_level3_uppercase_no_underline(self, heading3: LayoutBlock):
        output = render_plaintext([heading3])
        assert "DETAILS" in output
        # Level 3 should NOT have underlines
        assert "===" not in output
        assert "---" not in output

    def test_paragraph_double_newline(self, paragraph: LayoutBlock):
        output = render_plaintext([paragraph])
        assert "Some body text here." in output

    def test_list_item_has_dash_prefix(self, list_item: LayoutBlock):
        output = render_plaintext([list_item])
        assert "- First bullet" in output

    def test_combined_document(
        self,
        heading1: LayoutBlock,
        paragraph: LayoutBlock,
        list_item: LayoutBlock,
    ):
        output = render_plaintext([heading1, paragraph, list_item])
        assert "INTRODUCTION" in output
        assert "Some body text here." in output
        assert "- First bullet" in output

    def test_table_rendering(self, table_blocks: list[LayoutBlock]):
        output = render_plaintext(table_blocks)
        assert "| Name" in output
        assert "| Alice" in output
        # Separator row after header
        assert "|-" in output

    def test_page_break_marker(self):
        """Second page should trigger a page separator."""
        blocks = [
            _block(BlockType.PARAGRAPH, "Page 1 content", page_number=1),
            _block(BlockType.PARAGRAPH, "Page 2 content", page_number=2),
        ]
        output = render_plaintext(blocks)
        assert "--- Page 2 ---" in output


# ── Markdown renderer ─────────────────────────────────────────────────


class TestRenderMarkdown:
    def test_empty_blocks(self):
        assert render_markdown([]) == "\n"

    def test_heading_level1(self, heading1: LayoutBlock):
        output = render_markdown([heading1])
        assert output.startswith("# Introduction")

    def test_heading_level2(self, heading2: LayoutBlock):
        output = render_markdown([heading2])
        assert "## Background" in output

    def test_heading_level3(self, heading3: LayoutBlock):
        output = render_markdown([heading3])
        assert "### Details" in output

    def test_bold_span_gets_double_asterisks(self, bold_paragraph: LayoutBlock):
        output = render_markdown([bold_paragraph])
        assert "**Bold text**" in output

    def test_italic_span(self):
        block = _block(
            BlockType.PARAGRAPH,
            "Italic text",
            spans=[
                TextSpan(
                    text="Italic text",
                    font_name="Helvetica-Oblique",
                    font_size=12.0,
                    is_bold=False,
                    is_italic=True,
                )
            ],
        )
        output = render_markdown([block])
        assert "*Italic text*" in output

    def test_bold_italic_span(self):
        block = _block(
            BlockType.PARAGRAPH,
            "Both",
            spans=[
                TextSpan(
                    text="Both",
                    font_name="Helvetica-BoldOblique",
                    font_size=12.0,
                    is_bold=True,
                    is_italic=True,
                )
            ],
        )
        output = render_markdown([block])
        assert "***Both***" in output

    def test_list_item_prefix(self, list_item: LayoutBlock):
        output = render_markdown([list_item])
        assert "- First bullet" in output

    def test_table_gfm_pipes(self, table_blocks: list[LayoutBlock]):
        output = render_markdown(table_blocks)
        lines = output.strip().splitlines()
        # Header row
        header_line = [l for l in lines if "Name" in l]
        assert len(header_line) >= 1
        assert "|" in header_line[0]
        # Separator row with dashes
        separator_lines = [l for l in lines if "---" in l]
        assert len(separator_lines) >= 1

    def test_paragraph_plain_text(self, paragraph: LayoutBlock):
        output = render_markdown([paragraph])
        assert "Some body text here." in output


# ── LaTeX renderer ────────────────────────────────────────────────────


class TestRenderLatex:
    def test_empty_blocks(self):
        output = render_latex([])
        assert r"\documentclass{article}" in output
        assert r"\begin{document}" in output
        assert r"\end{document}" in output

    def test_preamble_present(self, heading1: LayoutBlock):
        output = render_latex([heading1])
        assert r"\documentclass{article}" in output
        assert r"\usepackage[utf8]{inputenc}" in output
        assert r"\usepackage{geometry,longtable,hyperref}" in output
        assert r"\begin{document}" in output
        assert r"\end{document}" in output

    def test_heading_level1_section(self, heading1: LayoutBlock):
        output = render_latex([heading1])
        assert r"\section{Introduction}" in output

    def test_heading_level2_subsection(self, heading2: LayoutBlock):
        output = render_latex([heading2])
        assert r"\subsection{Background}" in output

    def test_heading_level3_subsubsection(self, heading3: LayoutBlock):
        output = render_latex([heading3])
        assert r"\subsubsection{Details}" in output

    def test_list_items_produce_itemize(self):
        blocks = [
            _block(BlockType.LIST_ITEM, "- Alpha"),
            _block(BlockType.LIST_ITEM, "- Beta"),
        ]
        output = render_latex(blocks)
        assert r"\begin{itemize}" in output
        assert r"\end{itemize}" in output
        assert r"\item" in output

    def test_single_list_item_closes_itemize(self):
        blocks = [_block(BlockType.LIST_ITEM, "- Only one")]
        output = render_latex(blocks)
        assert r"\begin{itemize}" in output
        assert r"\end{itemize}" in output

    def test_special_chars_escaped(self):
        block = _block(BlockType.PARAGRAPH, "Price is $5 & 10% off #sale")
        output = render_latex([block])
        assert r"\$" in output
        assert r"\&" in output
        assert r"\%" in output
        assert r"\#" in output

    def test_underscore_escaped(self):
        block = _block(BlockType.PARAGRAPH, "my_variable")
        output = render_latex([block])
        assert r"my\_variable" in output

    def test_bold_span_textbf(self, bold_paragraph: LayoutBlock):
        output = render_latex([bold_paragraph])
        assert r"\textbf{" in output

    def test_italic_span_textit(self):
        block = _block(
            BlockType.PARAGRAPH,
            "Italic",
            spans=[
                TextSpan(
                    text="Italic",
                    font_name="Helvetica-Oblique",
                    font_size=12.0,
                    is_bold=False,
                    is_italic=True,
                )
            ],
        )
        output = render_latex([block])
        assert r"\textit{" in output

    def test_table_produces_longtable(self, table_blocks: list[LayoutBlock]):
        output = render_latex(table_blocks)
        assert r"\begin{longtable}" in output
        assert r"\end{longtable}" in output
        assert r"\hline" in output


# ── _escape_latex helper ──────────────────────────────────────────────


class TestEscapeLatex:
    def test_ampersand(self):
        assert _escape_latex("A & B") == r"A \& B"

    def test_percent(self):
        assert _escape_latex("100%") == r"100\%"

    def test_dollar(self):
        assert _escape_latex("$5") == r"\$5"

    def test_hash(self):
        assert _escape_latex("#1") == r"\#1"

    def test_underscore(self):
        assert _escape_latex("a_b") == r"a\_b"

    def test_tilde(self):
        assert _escape_latex("~") == r"\textasciitilde{}"

    def test_caret(self):
        assert _escape_latex("^") == r"\textasciicircum{}"

    def test_backslash(self):
        assert _escape_latex("\\") == r"\textbackslash{}"

    def test_braces(self):
        assert _escape_latex("{x}") == r"\{x\}"

    def test_plain_text_unchanged(self):
        assert _escape_latex("Hello World") == "Hello World"


# ── _group_table_cells ────────────────────────────────────────────────


class TestGroupTableCells:
    def test_single_row(self):
        cells = [
            _table_cell("A", 100.0, 0.0),
            _table_cell("B", 100.0, 100.0),
            _table_cell("C", 100.0, 200.0),
        ]
        rows = _group_table_cells(cells)
        assert len(rows) == 1
        assert len(rows[0]) == 3

    def test_two_rows(self):
        cells = [
            _table_cell("A", 100.0, 0.0),
            _table_cell("B", 100.0, 100.0),
            _table_cell("C", 120.0, 0.0),
            _table_cell("D", 120.0, 100.0),
        ]
        rows = _group_table_cells(cells)
        assert len(rows) == 2

    def test_empty_cells_list(self):
        rows = _group_table_cells([])
        assert rows == []

    def test_cells_at_similar_y_grouped(self):
        """Cells within Y_TOLERANCE should be in the same row."""
        cells = [
            _table_cell("A", 100.0, 0.0),
            _table_cell("B", 102.0, 100.0),  # within tolerance
        ]
        rows = _group_table_cells(cells)
        assert len(rows) == 1
