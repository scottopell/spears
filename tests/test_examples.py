"""Example-based tests against realistic fixture projects.

These complement the property tests: they check that the *messages* and
*shape* of audit/lint reports look right on hand-crafted specs that
exercise specific failure modes.
"""

from __future__ import annotations

from pathlib import Path

from spears.audit import audit, format_report as audit_report
from spears.lint import lint, format_report as lint_report

FIXTURES = Path(__file__).parent / "fixtures"


def test_lying_project_audit_default_flags_only_complete_unanchored():
    root = FIXTURES / "lying-project"
    result = audit(root=root)
    flagged = {f.req_id for f in result.findings}
    # REQ-RL-001: complete + has anchor in src/rate_limit.py -> not flagged.
    # REQ-RL-002: complete + no anchor -> flagged.
    # REQ-RL-003: in-progress -> excluded by default status filter.
    # REQ-RL-004: complete + no anchor -> flagged.
    assert flagged == {"REQ-RL-002", "REQ-RL-004"}, flagged
    assert not result.ok


def test_lying_project_audit_all_statuses_includes_in_progress():
    root = FIXTURES / "lying-project"
    result = audit(root=root, all_statuses=True)
    flagged = {f.req_id for f in result.findings}
    assert "REQ-RL-003" in flagged
    assert "REQ-RL-001" not in flagged  # has anchor


def test_lying_project_lint_catches_known_issues():
    root = FIXTURES / "lying-project"
    result = lint(root=root)
    by_rule: dict[str, set[str | None]] = {}
    for i in result.issues:
        by_rule.setdefault(i.rule, set()).add(i.req_id)
    # R1: REQ-RL-003 ("Caching Strategy") starts with a gerund.
    assert "REQ-RL-003" in by_rule.get("R1", set())
    # R2: REQ-RL-003 has no Rationale block.
    assert "REQ-RL-003" in by_rule.get("R2", set())
    # R3: REQ-RL-004's status row has 4 cells where the header has 3.
    assert "REQ-RL-004" in by_rule.get("R3", set())


def test_clean_project_is_clean():
    root = FIXTURES / "clean-project"
    audit_result = audit(root=root)
    assert audit_result.ok, audit_report(audit_result, root)
    lint_result = lint(root=root)
    assert lint_result.ok, lint_report(lint_result, root)


def test_audit_report_text_contains_req_and_path(tmp_path):
    # Just the smoke that format_report doesn't crash on real findings.
    root = FIXTURES / "lying-project"
    result = audit(root=root)
    text = audit_report(result, root)
    assert "REQ-RL-002" in text
    assert "rate-limiting" in text
    assert "specs/rate-limiting/executive.md" in text
