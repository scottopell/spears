"""Property-based tests for spears.lint.

The two structural rules (R2 Rationale presence, R3 status-table column
shape) have a clean property-based formulation: their issue counts must
match the size of the offending population exactly.

R1 (verb titles) is checked with a smaller, targeted set of examples in
test_lint_examples.py because the heuristic is intentionally narrow.
"""

from __future__ import annotations

from pathlib import Path

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from spears.lint import lint
from tests.strategies import (
    render_heading,
    render_status_row,
    req_ids,
    status_symbols,
    titles,
)


def _write_full_spec(
    root: Path,
    name: str,
    headings_with_rationale: list[tuple[str, str, bool]],
    extra_status_rows: list[tuple[str, str, str, int]] | None = None,
    table_header_columns: int = 2,
) -> None:
    spec_dir = root / "specs" / name
    spec_dir.mkdir(parents=True, exist_ok=True)
    req_lines = ["# Requirements", ""]
    for rid, title, has_rationale in headings_with_rationale:
        req_lines.append(render_heading(rid, title))
        if has_rationale:
            req_lines.append("**Rationale:** Because users care.")
        req_lines.append("")
    (spec_dir / "requirements.md").write_text("\n".join(req_lines), encoding="utf-8")
    (spec_dir / "design.md").write_text("# Design\n", encoding="utf-8")

    header = ["Col" + str(i) for i in range(table_header_columns)]
    sep = ["---"] * table_header_columns
    table_lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(sep) + " |",
    ]
    for rid, title, has_rationale in headings_with_rationale:
        # Default: a properly-shaped row with table_header_columns cells.
        extras = ["x"] * (table_header_columns - 2)
        table_lines.append(render_status_row(rid, title, "✅", extras))
    if extra_status_rows:
        for rid, title, sym, ncols in extra_status_rows:
            extras = ["x"] * max(0, ncols - 2)
            table_lines.append(render_status_row(rid, title, sym, extras))
    (spec_dir / "executive.md").write_text(
        "# Executive\n\n## Status\n\n" + "\n".join(table_lines) + "\n",
        encoding="utf-8",
    )


@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(
    st.lists(
        st.tuples(req_ids, titles, st.booleans()),
        min_size=1,
        max_size=6,
        unique_by=lambda t: t[0],
    )
)
def test_R2_flags_exactly_the_reqs_missing_rationale(tmp_path_factory, headings):
    root = tmp_path_factory.mktemp("root")
    _write_full_spec(root, "demo", headings)
    result = lint(root=root)
    flagged_R2 = {i.req_id for i in result.issues if i.rule == "R2"}
    expected = {rid for rid, _, has_rat in headings if not has_rat}
    assert flagged_R2 == expected


@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(
    st.lists(
        st.tuples(req_ids, titles),
        min_size=1,
        max_size=4,
        unique_by=lambda t: t[0],
    ),
    st.lists(
        st.tuples(req_ids, titles, status_symbols, st.integers(min_value=2, max_value=6)),
        min_size=1,
        max_size=4,
        unique_by=lambda t: t[0],
    ),
    st.integers(min_value=2, max_value=6),
)
def test_R3_flags_only_rows_whose_column_count_differs(
    tmp_path_factory, base, extras, header_cols
):
    root = tmp_path_factory.mktemp("root")
    base_with_rationale = [(rid, title, True) for rid, title in base]
    # Ensure no overlap between base and extras IDs (would dedupe to a
    # single declaration and confuse the assertion).
    base_ids = {rid for rid, _ in base}
    extras = [(rid, t, s, n) for rid, t, s, n in extras if rid not in base_ids]
    _write_full_spec(
        root,
        "demo",
        base_with_rationale,
        extra_status_rows=extras,
        table_header_columns=header_cols,
    )
    result = lint(root=root)
    r3 = [i for i in result.issues if i.rule == "R3"]
    expected_offenders = {rid for rid, _, _, n in extras if n != header_cols}
    actual_offenders = {i.req_id for i in r3}
    assert actual_offenders == expected_offenders
