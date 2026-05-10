"""Hypothesis strategies for spEARS-shaped data.

The strategies here generate the textual building blocks that the parser
consumes -- REQ ids, headings, status-table rows, full status tables -- so
property tests can assert round-trip and structural invariants.
"""

from __future__ import annotations

from hypothesis import strategies as st

from spears.parser import STATUS_SYMBOLS

# REQ-[ABBREV]-NNN where ABBREV starts with a letter and is letters+digits,
# and NNN is one or more digits.
abbreviations = st.text(
    alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=4
).flatmap(
    lambda head: st.text(
        alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", min_size=0, max_size=4
    ).map(lambda tail: head + tail)
)

req_numbers = st.integers(min_value=1, max_value=9999).map(lambda n: f"{n:03d}")

req_ids = st.builds(lambda a, n: f"REQ-{a}-{n}", abbreviations, req_numbers)

# Titles avoid characters that would break our markdown encoding (newlines,
# pipes, asterisks). Realistic titles are short prose.
title_chars = st.characters(
    blacklist_characters="\r\n|*_`<>",
    blacklist_categories=("Cs", "Cc"),
)
titles = st.text(alphabet=title_chars, min_size=1, max_size=60).map(str.strip).filter(
    lambda s: bool(s) and not s.startswith("#")
)

status_symbols = st.sampled_from(sorted(STATUS_SYMBOLS.keys()))

# A free-form table cell value (no pipes / newlines / leading-trailing
# whitespace that would confuse split).
cell_chars = st.characters(
    blacklist_characters="\r\n|",
    blacklist_categories=("Cs", "Cc"),
)
cells = st.text(alphabet=cell_chars, min_size=0, max_size=20).map(str.strip)


def render_heading(req_id: str, title: str) -> str:
    return f"### {req_id}: {title}"


def render_status_row(req_id: str, title: str, symbol: str, extra: list[str]) -> str:
    cells_out = [f"**{req_id}:** {title}", f"{symbol} something"]
    cells_out.extend(extra)
    return "| " + " | ".join(cells_out) + " |"


def render_status_table(rows: list[tuple[str, str, str, list[str]]]) -> str:
    """Render a complete markdown table.

    Each row is (req_id, title, status_symbol, extra_cells). All rows must
    share the same number of extra_cells so the table is well-shaped.
    """
    if not rows:
        return ""
    extra_count = len(rows[0][3])
    header_cells = ["Requirement", "Status"] + [f"Col{i+3}" for i in range(extra_count)]
    sep_cells = ["---"] * len(header_cells)
    lines = [
        "| " + " | ".join(header_cells) + " |",
        "| " + " | ".join(sep_cells) + " |",
    ]
    for req_id, title, sym, extra in rows:
        lines.append(render_status_row(req_id, title, sym, extra))
    return "\n".join(lines)
