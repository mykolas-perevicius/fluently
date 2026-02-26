"""
PDF layout extraction using PyMuPDF.

Extracts structured blocks (headings, paragraphs, lists, table cells)
from PDF files, preserving font metadata for downstream formatting.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from enum import StrEnum

import fitz  # PyMuPDF


class BlockType(StrEnum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST_ITEM = "list_item"
    TABLE_CELL = "table_cell"


@dataclass
class TextSpan:
    text: str
    font_name: str
    font_size: float
    is_bold: bool
    is_italic: bool


@dataclass
class LayoutBlock:
    block_type: BlockType
    text: str
    spans: list[TextSpan]
    bbox: tuple[float, float, float, float]
    page_number: int
    heading_level: int = 0  # 1-3, 0 = not heading
    indent_level: int = 0


@dataclass
class DocumentLayout:
    blocks: list[LayoutBlock]
    page_count: int


_LIST_PATTERN_PREFIXES = ("- ", "* ", "• ")


def _is_list_item(text: str) -> bool:
    """Check if text starts with a list marker."""
    stripped = text.lstrip()
    if any(stripped.startswith(p) for p in _LIST_PATTERN_PREFIXES):
        return True
    # Numbered list: "1. " or "1) "
    for i, ch in enumerate(stripped):
        if ch.isdigit():
            continue
        if i > 0 and ch in ".)" and len(stripped) > i + 1 and stripped[i + 1] == " ":
            return True
        break
    return False


def _compute_modal_font_size(raw_blocks: list[dict]) -> float:
    """Find the most common font size (body text) across all spans."""
    size_counter: Counter[float] = Counter()
    for block in raw_blocks:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                if text:
                    size_counter[round(span["size"], 1)] += len(text)
    if not size_counter:
        return 12.0
    return size_counter.most_common(1)[0][0]


def _classify_heading_level(
    font_size: float, modal_size: float, ranked_sizes: list[float]
) -> int:
    """Classify heading level based on font size relative to body text."""
    if font_size < modal_size * 1.3:
        return 0
    if ranked_sizes and font_size >= ranked_sizes[0]:
        return 1
    if len(ranked_sizes) > 1 and font_size >= ranked_sizes[1]:
        return 2
    return 3


def _detect_table_rows(
    blocks: list[dict], page_number: int, modal_size: float
) -> list[list[LayoutBlock]]:
    """Detect table rows using spatial heuristic: 3+ blocks at similar y-positions."""
    Y_TOLERANCE = 5.0  # points

    # Group blocks by approximate y-position (top of bbox)
    y_groups: dict[float, list[dict]] = {}
    for block in blocks:
        if block.get("type") != 0:  # text blocks only
            continue
        y_top = round(block["bbox"][1] / Y_TOLERANCE) * Y_TOLERANCE
        y_groups.setdefault(y_top, []).append(block)

    table_rows: list[list[LayoutBlock]] = []
    for _y, group in sorted(y_groups.items()):
        if len(group) < 3:
            continue
        # Sort by x-position (left edge)
        group.sort(key=lambda b: b["bbox"][0])
        row: list[LayoutBlock] = []
        for block in group:
            text_parts = []
            spans = []
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    t = span.get("text", "")
                    if t.strip():
                        text_parts.append(t)
                        flags = span.get("flags", 0)
                        spans.append(
                            TextSpan(
                                text=t,
                                font_name=span.get("font", ""),
                                font_size=span.get("size", modal_size),
                                is_bold=bool(flags & (1 << 4)),
                                is_italic=bool(flags & (1 << 1)),
                            )
                        )
            cell_text = " ".join(text_parts).strip()
            if cell_text:
                row.append(
                    LayoutBlock(
                        block_type=BlockType.TABLE_CELL,
                        text=cell_text,
                        spans=spans,
                        bbox=tuple(block["bbox"]),
                        page_number=page_number,
                    )
                )
        if len(row) >= 3:
            table_rows.append(row)
    return table_rows


def extract_layout(pdf_bytes: bytes) -> DocumentLayout:
    """Extract structured layout from a PDF file."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    all_blocks: list[LayoutBlock] = []

    # First pass: collect all raw blocks and compute modal font size
    all_raw_blocks: list[dict] = []
    for page in doc:
        page_dict = page.get_text("dict")
        all_raw_blocks.extend(page_dict.get("blocks", []))

    modal_size = _compute_modal_font_size(all_raw_blocks)

    # Compute ranked heading sizes for level classification
    heading_sizes: set[float] = set()
    for block in all_raw_blocks:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                size = round(span.get("size", 0), 1)
                if size >= modal_size * 1.3 and span.get("text", "").strip():
                    heading_sizes.add(size)
    ranked_sizes = sorted(heading_sizes, reverse=True)

    # Second pass: classify blocks per page
    for page_idx, page in enumerate(doc):
        page_number = page_idx + 1
        page_dict = page.get_text("dict")
        raw_blocks = page_dict.get("blocks", [])

        # Detect table rows (blocks that are part of tables)
        table_rows = _detect_table_rows(raw_blocks, page_number, modal_size)
        table_block_bboxes: set[tuple[float, ...]] = set()
        for row in table_rows:
            for cell in row:
                table_block_bboxes.add(cell.bbox)
            all_blocks.extend(row)

        # Process non-table text blocks
        page_left = float("inf")
        for block in raw_blocks:
            if block.get("type") == 0:
                page_left = min(page_left, block["bbox"][0])

        for block in raw_blocks:
            if block.get("type") != 0:  # skip image blocks
                continue

            bbox = tuple(block["bbox"])
            if bbox in table_block_bboxes:
                continue

            text_parts: list[str] = []
            spans: list[TextSpan] = []
            dominant_size = modal_size

            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    t = span.get("text", "")
                    if not t.strip():
                        continue
                    text_parts.append(t)
                    flags = span.get("flags", 0)
                    spans.append(
                        TextSpan(
                            text=t,
                            font_name=span.get("font", ""),
                            font_size=span.get("size", modal_size),
                            is_bold=bool(flags & (1 << 4)),
                            is_italic=bool(flags & (1 << 1)),
                        )
                    )
                    # Use largest span size as dominant
                    if span.get("size", 0) > dominant_size:
                        dominant_size = span["size"]

            full_text = " ".join(text_parts).strip()
            if not full_text:
                continue

            # Classify block type
            heading_level = _classify_heading_level(
                dominant_size, modal_size, ranked_sizes
            )

            # Calculate indent level from x-position
            x_left = block["bbox"][0]
            indent_level = max(0, round((x_left - page_left) / 36))  # ~0.5 inch steps

            if heading_level > 0:
                block_type = BlockType.HEADING
            elif _is_list_item(full_text):
                block_type = BlockType.LIST_ITEM
            else:
                block_type = BlockType.PARAGRAPH

            all_blocks.append(
                LayoutBlock(
                    block_type=block_type,
                    text=full_text,
                    spans=spans,
                    bbox=bbox,
                    page_number=page_number,
                    heading_level=heading_level,
                    indent_level=indent_level,
                )
            )

    page_count = len(doc)
    doc.close()
    return DocumentLayout(blocks=all_blocks, page_count=page_count)
