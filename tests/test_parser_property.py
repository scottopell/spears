"""Property-based tests for spears.parser.

The parser is the load-bearing piece: if a declaration pattern fails to
parse, audit and lint will both make wrong claims. These tests fuzz the
two canonical declaration patterns plus the table-cell splitter and
status-symbol classifier.
"""

from __future__ import annotations

import re

from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from spears.parser import (
    REQ_HEADING_RE,
    REQ_ID_RE,
    REQ_STATUS_ROW_RE,
    STATUS_SYMBOLS,
    _classify_status,
    _split_table_row,
    parse_requirements,
    parse_status_table,
)
from tests.strategies import (
    cells,
    render_heading,
    render_status_row,
    render_status_table,
    req_ids,
    status_symbols,
    titles,
)


# ---------------------------------------------------------------------------
# REQ_ID_RE
# ---------------------------------------------------------------------------

@given(req_ids)
def test_req_id_regex_matches_generated_ids(req_id):
    assert REQ_ID_RE.fullmatch(req_id), req_id


@given(req_ids, st.text(min_size=0, max_size=30), st.text(min_size=0, max_size=30))
def test_req_id_regex_finds_id_in_surrounding_text(req_id, before, after):
    # Surround the ID with text that does NOT contain another REQ-style
    # token, so the unique match assertion holds.
    assume(not REQ_ID_RE.search(before) and not REQ_ID_RE.search(after))
    # Also avoid extending the ID rightward: the regex's `\d+` is greedy, so
    # if `after` begins with a digit it would extend the number.
    assume(not after[:1].isdigit())
    haystack = before + req_id + after
    matches = REQ_ID_RE.findall(haystack)
    assert matches == [req_id], (haystack, matches)


# ---------------------------------------------------------------------------
# REQ heading
# ---------------------------------------------------------------------------

@given(req_ids, titles)
def test_heading_round_trip(req_id, title):
    line = render_heading(req_id, title)
    m = REQ_HEADING_RE.match(line)
    assert m, line
    assert m.group(1) == req_id
    assert m.group(2) == title.strip()


# ---------------------------------------------------------------------------
# REQ status-table row
# ---------------------------------------------------------------------------

@given(req_ids, titles, status_symbols, st.lists(cells, min_size=0, max_size=3))
def test_status_row_round_trip(req_id, title, symbol, extra):
    line = render_status_row(req_id, title, symbol, extra)
    cells_out = _split_table_row(line)
    # Always at least: REQ cell, status cell.
    assert len(cells_out) >= 2
    first = cells_out[0]
    m = REQ_STATUS_ROW_RE.match(f"| {first} |")
    assert m, first
    assert m.group(1) == req_id


@given(req_ids, titles, status_symbols, st.lists(cells, min_size=0, max_size=3))
def test_status_row_classify_status(req_id, title, symbol, extra):
    line = render_status_row(req_id, title, symbol, extra)
    cells_out = _split_table_row(line)
    sym, status = _classify_status(cells_out[1])
    assert status == STATUS_SYMBOLS[symbol]


# ---------------------------------------------------------------------------
# _split_table_row
# ---------------------------------------------------------------------------

@given(st.lists(cells, min_size=1, max_size=8))
def test_split_table_row_preserves_count(parts):
    # Render and re-split; count must round-trip.
    line = "| " + " | ".join(parts) + " |"
    out = _split_table_row(line)
    assert len(out) == len(parts), (line, out, parts)


@given(st.text(min_size=0, max_size=30))
def test_split_table_row_rejects_non_pipe(line):
    assume(not line.lstrip().startswith("|"))
    assert _split_table_row(line) == []


# ---------------------------------------------------------------------------
# _classify_status
# ---------------------------------------------------------------------------

@given(status_symbols, st.text(alphabet=st.characters(blacklist_characters="✅🔄⏭❌⚠️", blacklist_categories=("Cs", "Cc")), min_size=0, max_size=20))
def test_classify_status_finds_symbol(symbol, padding):
    cell = padding + " " + symbol + " " + padding
    sym, status = _classify_status(cell)
    assert status == STATUS_SYMBOLS[symbol]


# ---------------------------------------------------------------------------
# parse_requirements: every generated heading is recovered.
# ---------------------------------------------------------------------------

@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(
    st.lists(
        st.tuples(req_ids, titles),
        min_size=1,
        max_size=8,
        unique_by=lambda pair: pair[0],
    )
)
def test_parse_requirements_round_trip(tmp_path_factory, pairs):
    body_lines: list[str] = ["# Requirements", ""]
    for req_id, title in pairs:
        body_lines.append(render_heading(req_id, title))
        body_lines.append("")
        body_lines.append("**Rationale:** A user benefit.")
        body_lines.append("")
    path = tmp_path_factory.mktemp("req") / "requirements.md"
    path.write_text("\n".join(body_lines), encoding="utf-8")
    parsed = parse_requirements(path)
    parsed_ids = [r.req_id for r in parsed]
    assert parsed_ids == [p[0] for p in pairs]
    for r in parsed:
        assert r.rationale_present, r.req_id


# ---------------------------------------------------------------------------
# parse_status_table: every generated row is recovered with correct status.
# ---------------------------------------------------------------------------

@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(
    st.integers(min_value=0, max_value=2).flatmap(
        lambda n_extra: st.lists(
            st.tuples(req_ids, titles, status_symbols),
            min_size=1,
            max_size=8,
            unique_by=lambda t: t[0],
        ).map(lambda rows: (n_extra, rows))
    )
)
def test_parse_status_table_round_trip(tmp_path_factory, payload):
    n_extra, rows = payload
    full_rows = [(rid, title, sym, ["x"] * n_extra) for rid, title, sym in rows]
    table_md = render_status_table(full_rows)
    text = "# Executive\n\n## Status\n\n" + table_md + "\n"
    path = tmp_path_factory.mktemp("exec") / "executive.md"
    path.write_text(text, encoding="utf-8")
    table = parse_status_table(path)
    assert table is not None
    assert table.column_count == 2 + n_extra
    parsed_ids = [r.req_id for r in table.rows]
    assert parsed_ids == [r[0] for r in full_rows]
    for parsed, (rid, title, sym, _) in zip(table.rows, full_rows):
        assert parsed.req_id == rid
        assert parsed.status == STATUS_SYMBOLS[sym]
        assert parsed.column_count == table.column_count
