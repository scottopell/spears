"""Property-based tests for spears.audit.

The two invariants worth fuzzing:
  1. A REQ whose only mentions are inside specs/ is *always* unanchored.
     (Otherwise the v1 prototype's noisy verbose mode was actually right
     and the canonical-declaration filter is meaningless.)
  2. The status filter is honored: a REQ with status X is never reported
     when X is not in the filter set.
"""

from __future__ import annotations

from pathlib import Path

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from spears.audit import audit
from spears.parser import STATUS_SYMBOLS
from tests.strategies import (
    render_heading,
    render_status_table,
    req_ids,
    status_symbols,
    titles,
)


def _write_spec(
    root: Path,
    name: str,
    rows: list[tuple[str, str, str]],
    code_anchored_ids: list[str],
) -> None:
    """Build a spec dir under root/specs/<name> with optional code anchors."""
    spec_dir = root / "specs" / name
    spec_dir.mkdir(parents=True, exist_ok=True)
    req_lines = ["# Requirements", ""]
    for rid, title, _ in rows:
        req_lines.append(render_heading(rid, title))
        req_lines.append("**Rationale:** A user benefit.")
        req_lines.append("")
    (spec_dir / "requirements.md").write_text("\n".join(req_lines), encoding="utf-8")
    (spec_dir / "design.md").write_text("# Design\n", encoding="utf-8")
    table = render_status_table([(rid, t, s, []) for rid, t, s in rows])
    (spec_dir / "executive.md").write_text(
        "# Executive\n\n## Status\n\n" + table + "\n", encoding="utf-8"
    )
    if code_anchored_ids:
        src = root / "src"
        src.mkdir(exist_ok=True)
        body = "\n".join(f"// {rid}: anchor" for rid in code_anchored_ids)
        (src / "impl.py").write_text(body, encoding="utf-8")


@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(
    st.lists(
        st.tuples(req_ids, titles, status_symbols),
        min_size=1,
        max_size=6,
        unique_by=lambda t: t[0],
    )
)
def test_no_code_anchors_means_every_complete_req_is_unanchored(
    tmp_path_factory, rows
):
    root = tmp_path_factory.mktemp("root")
    _write_spec(root, "demo", rows, code_anchored_ids=[])
    result = audit(root=root)  # default: complete only
    expected_ids = {
        rid for rid, _, sym in rows if STATUS_SYMBOLS[sym] == "complete"
    }
    found_ids = {f.req_id for f in result.findings}
    assert found_ids == expected_ids


@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(
    st.lists(
        st.tuples(req_ids, titles, status_symbols),
        min_size=1,
        max_size=6,
        unique_by=lambda t: t[0],
    )
)
def test_all_code_anchored_means_no_findings(tmp_path_factory, rows):
    root = tmp_path_factory.mktemp("root")
    all_ids = [rid for rid, _, _ in rows]
    _write_spec(root, "demo", rows, code_anchored_ids=all_ids)
    result = audit(root=root, all_statuses=True)
    assert result.findings == [], result.findings


@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(
    st.lists(
        st.tuples(req_ids, titles, status_symbols),
        min_size=1,
        max_size=6,
        unique_by=lambda t: t[0],
    ),
    st.sets(
        st.sampled_from(
            ["complete", "in-progress", "planned", "not-started", "manual"]
        ),
        min_size=1,
        max_size=5,
    ),
)
def test_status_filter_is_honored(tmp_path_factory, rows, allowed):
    root = tmp_path_factory.mktemp("root")
    _write_spec(root, "demo", rows, code_anchored_ids=[])
    result = audit(root=root, statuses=allowed)
    for f in result.findings:
        assert f.status in allowed, (f.status, allowed)
    expected_ids = {
        rid for rid, _, sym in rows if STATUS_SYMBOLS[sym] in allowed
    }
    found_ids = {f.req_id for f in result.findings}
    assert found_ids == expected_ids
