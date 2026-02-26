"""
Format renderers for translated document blocks.

Three pure functions that take a list of LayoutBlocks (already translated)
and produce plaintext, Markdown, or LaTeX output.
"""

from __future__ import annotations

import re
from itertools import groupby
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils.pdf_layout import LayoutBlock

from utils.pdf_layout import BlockType

# ── LaTeX special character escaping ────────────────────────────────
_LATEX_SPECIAL = re.compile(r"([&%$#_{}~^\\])")
_LATEX_REPLACEMENTS = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "\\": r"\textbackslash{}",
}


def _escape_latex(text: str) -> str:
    return _LATEX_SPECIAL.sub(lambda m: _LATEX_REPLACEMENTS[m.group(1)], text)


# ── Table grouping helper ──────────────────────────────────────────

Y_TOLERANCE = 5.0


def _group_table_cells(
    blocks: list[LayoutBlock],
) -> list[list[LayoutBlock]]:
    """Group consecutive TABLE_CELL blocks into rows by y-position."""
    rows: list[list[LayoutBlock]] = []
    current_y: float | None = None
    current_row: list[LayoutBlock] = []

    for block in blocks:
        y_top = round(block.bbox[1] / Y_TOLERANCE) * Y_TOLERANCE
        if current_y is None or abs(y_top - current_y) > Y_TOLERANCE:
            if current_row:
                rows.append(current_row)
            current_row = [block]
            current_y = y_top
        else:
            current_row.append(block)

    if current_row:
        rows.append(current_row)

    return rows


# ── Plaintext renderer ─────────────────────────────────────────────


def render_plaintext(blocks: list[LayoutBlock]) -> str:
    """Render blocks as formatted plaintext with ASCII art tables."""
    lines: list[str] = []
    current_page = 0
    i = 0

    while i < len(blocks):
        block = blocks[i]

        # Page break marker
        if block.page_number != current_page:
            if current_page > 0:
                lines.append("")
                lines.append(f"--- Page {block.page_number} ---")
                lines.append("")
            current_page = block.page_number

        if block.block_type == BlockType.HEADING:
            lines.append("")
            if block.heading_level == 1:
                lines.append(block.text.upper())
                lines.append("=" * len(block.text))
            elif block.heading_level == 2:
                lines.append(block.text)
                lines.append("-" * len(block.text))
            else:
                lines.append(block.text.upper())
            lines.append("")
            i += 1

        elif block.block_type == BlockType.LIST_ITEM:
            indent = "  " * block.indent_level
            lines.append(f"{indent}- {block.text.lstrip('- *•').strip()}")
            i += 1

        elif block.block_type == BlockType.TABLE_CELL:
            # Collect all consecutive table cells
            table_cells: list[LayoutBlock] = []
            while i < len(blocks) and blocks[i].block_type == BlockType.TABLE_CELL:
                table_cells.append(blocks[i])
                i += 1

            rows = _group_table_cells(table_cells)
            if rows:
                # Calculate column widths
                num_cols = max(len(row) for row in rows)
                col_widths = [0] * num_cols
                for row in rows:
                    for ci, cell in enumerate(row):
                        col_widths[ci] = max(col_widths[ci], len(cell.text))

                # Render pipe-aligned table
                lines.append("")
                for ri, row in enumerate(rows):
                    cells = [
                        cell.text.ljust(col_widths[ci]) if ci < len(col_widths) else cell.text
                        for ci, cell in enumerate(row)
                    ]
                    # Pad missing columns
                    while len(cells) < num_cols:
                        cells.append(" " * col_widths[len(cells)])
                    lines.append("| " + " | ".join(cells) + " |")

                    if ri == 0:
                        lines.append(
                            "|-" + "-|-".join("-" * w for w in col_widths) + "-|"
                        )
                lines.append("")
            continue  # already incremented i

        else:  # PARAGRAPH
            lines.append(block.text)
            lines.append("")
            i += 1

    return "\n".join(lines).strip() + "\n"


# ── Markdown renderer ──────────────────────────────────────────────


def _md_inline(block: LayoutBlock) -> str:
    """Apply bold/italic to text based on span metadata."""
    if not block.spans:
        return block.text

    parts: list[str] = []
    for span in block.spans:
        text = span.text
        if span.is_bold and span.is_italic:
            text = f"***{text}***"
        elif span.is_bold:
            text = f"**{text}**"
        elif span.is_italic:
            text = f"*{text}*"
        parts.append(text)
    return " ".join(parts)


def render_markdown(blocks: list[LayoutBlock]) -> str:
    """Render blocks as GitHub-Flavored Markdown."""
    lines: list[str] = []
    i = 0

    while i < len(blocks):
        block = blocks[i]

        if block.block_type == BlockType.HEADING:
            prefix = "#" * min(block.heading_level, 3)
            lines.append(f"{prefix} {block.text}")
            lines.append("")
            i += 1

        elif block.block_type == BlockType.LIST_ITEM:
            text = block.text.lstrip("- *•").strip()
            # Detect numbered lists
            stripped = block.text.lstrip()
            if stripped and stripped[0].isdigit():
                lines.append(f"{block.text.lstrip()}")
            else:
                indent = "  " * block.indent_level
                lines.append(f"{indent}- {text}")
            i += 1

        elif block.block_type == BlockType.TABLE_CELL:
            table_cells: list[LayoutBlock] = []
            while i < len(blocks) and blocks[i].block_type == BlockType.TABLE_CELL:
                table_cells.append(blocks[i])
                i += 1

            rows = _group_table_cells(table_cells)
            if rows:
                num_cols = max(len(row) for row in rows)

                lines.append("")
                for ri, row in enumerate(rows):
                    cells = [cell.text for cell in row]
                    while len(cells) < num_cols:
                        cells.append("")
                    lines.append("| " + " | ".join(cells) + " |")
                    if ri == 0:
                        lines.append("| " + " | ".join("---" for _ in range(num_cols)) + " |")
                lines.append("")
            continue

        else:  # PARAGRAPH
            lines.append(_md_inline(block))
            lines.append("")
            i += 1

    return "\n".join(lines).strip() + "\n"


# ── LaTeX renderer ─────────────────────────────────────────────────


def render_latex(blocks: list[LayoutBlock]) -> str:
    """Render blocks as a compilable LaTeX document."""
    preamble = [
        r"\documentclass{article}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage{geometry,longtable,hyperref}",
        r"\begin{document}",
        "",
    ]

    body: list[str] = []
    i = 0
    in_itemize = False

    while i < len(blocks):
        block = blocks[i]
        escaped = _escape_latex(block.text)

        if block.block_type == BlockType.HEADING:
            if in_itemize:
                body.append(r"\end{itemize}")
                in_itemize = False
            if block.heading_level == 1:
                body.append(f"\\section{{{escaped}}}")
            elif block.heading_level == 2:
                body.append(f"\\subsection{{{escaped}}}")
            else:
                body.append(f"\\subsubsection{{{escaped}}}")
            body.append("")
            i += 1

        elif block.block_type == BlockType.LIST_ITEM:
            if not in_itemize:
                body.append(r"\begin{itemize}")
                in_itemize = True
            text = block.text.lstrip("- *•").strip()
            body.append(f"  \\item {_escape_latex(text)}")
            # Check if next block is still a list item
            if i + 1 >= len(blocks) or blocks[i + 1].block_type != BlockType.LIST_ITEM:
                body.append(r"\end{itemize}")
                body.append("")
                in_itemize = False
            i += 1

        elif block.block_type == BlockType.TABLE_CELL:
            if in_itemize:
                body.append(r"\end{itemize}")
                in_itemize = False

            table_cells: list[LayoutBlock] = []
            while i < len(blocks) and blocks[i].block_type == BlockType.TABLE_CELL:
                table_cells.append(blocks[i])
                i += 1

            rows = _group_table_cells(table_cells)
            if rows:
                num_cols = max(len(row) for row in rows)
                col_spec = "|".join(["l"] * num_cols)
                body.append(f"\\begin{{longtable}}{{|{col_spec}|}}")
                body.append(r"\hline")
                for ri, row in enumerate(rows):
                    cells = [_escape_latex(cell.text) for cell in row]
                    while len(cells) < num_cols:
                        cells.append("")
                    body.append(" & ".join(cells) + r" \\")
                    body.append(r"\hline")
                body.append(r"\end{longtable}")
                body.append("")
            continue

        else:  # PARAGRAPH
            if in_itemize:
                body.append(r"\end{itemize}")
                in_itemize = False

            # Apply inline formatting
            parts: list[str] = []
            if block.spans:
                for span in block.spans:
                    t = _escape_latex(span.text)
                    if span.is_bold and span.is_italic:
                        t = f"\\textbf{{\\textit{{{t}}}}}"
                    elif span.is_bold:
                        t = f"\\textbf{{{t}}}"
                    elif span.is_italic:
                        t = f"\\textit{{{t}}}"
                    parts.append(t)
                body.append(" ".join(parts))
            else:
                body.append(escaped)
            body.append("")
            i += 1

    if in_itemize:
        body.append(r"\end{itemize}")

    postamble = ["", r"\end{document}"]

    return "\n".join(preamble + body + postamble) + "\n"
