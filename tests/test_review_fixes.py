"""Tests for behaviours added in response to the PR #5 Copilot review.

These pin:
  - find_mentions honours its prune_dirs override (PR #5 r3214862081)
  - audit's all_statuses default includes ``n-a`` (PR #5 r3214862092)
  - --status validates against the known vocabulary (PR #5 r3214862105/2112)
  - --root must be a directory, not just exist (PR #5 r3214862134)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from spears.audit import ALL_STATUSES, audit
from spears.cli import UsageError, _parse_status_arg, main
from spears.scanner import find_mentions


def test_find_mentions_honours_prune_dirs_override(tmp_path):
    # A custom-pruned dir name that defaults would NOT prune.
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "keep.py").write_text("# REQ-AB-001: keep", encoding="utf-8")
    (tmp_path / "custom_skip").mkdir()
    (tmp_path / "custom_skip" / "skip.py").write_text(
        "# REQ-AB-002: skip", encoding="utf-8"
    )

    # Default pruning: both visible.
    default = find_mentions(tmp_path)
    assert "REQ-AB-001" in default
    assert "REQ-AB-002" in default

    # Custom pruning: only the kept one is visible.
    custom = find_mentions(tmp_path, prune_dirs={"custom_skip"})
    assert "REQ-AB-001" in custom
    assert "REQ-AB-002" not in custom


def test_audit_all_statuses_includes_n_a(tmp_path):
    spec = tmp_path / "specs" / "feat"
    spec.mkdir(parents=True)
    (spec / "requirements.md").write_text(
        "### REQ-NA-001: Skip Logging\n\n**Rationale:** users care.\n",
        encoding="utf-8",
    )
    (spec / "design.md").write_text("# Design\n", encoding="utf-8")
    (spec / "executive.md").write_text(
        "# Exec\n\n## Status\n\n"
        "| Req | Status |\n| --- | --- |\n"
        "| **REQ-NA-001:** Skip Logging | N/A | not applicable |\n",
        encoding="utf-8",
    )
    # Without all_statuses, n-a is excluded by the default complete-only set.
    default_result = audit(root=tmp_path)
    assert "REQ-NA-001" not in {f.req_id for f in default_result.findings}
    # With all_statuses, n-a IS included so a true unanchored n-a row shows.
    all_result = audit(root=tmp_path, all_statuses=True)
    assert "REQ-NA-001" in {f.req_id for f in all_result.findings}


@pytest.mark.parametrize("token", sorted(ALL_STATUSES))
def test_parse_status_arg_accepts_every_known_token(token):
    assert _parse_status_arg(token) == {token}


def test_parse_status_arg_normalises_case_and_whitespace():
    out = _parse_status_arg("  Complete , IN-PROGRESS ,n-a")
    assert out == {"complete", "in-progress", "n-a"}


def test_parse_status_arg_rejects_unknown_tokens():
    with pytest.raises(UsageError):
        _parse_status_arg("complet")  # typo
    with pytest.raises(UsageError):
        _parse_status_arg("complete,nonsense")


def test_parse_status_arg_none_for_empty_or_missing():
    assert _parse_status_arg(None) is None
    assert _parse_status_arg("") is None


def test_parse_status_arg_rejects_whitespace_or_comma_only():
    # PR #5 r3214892218: --status '   ' or ',' silently disabled reporting.
    with pytest.raises(UsageError):
        _parse_status_arg("   ")
    with pytest.raises(UsageError):
        _parse_status_arg(",")
    with pytest.raises(UsageError):
        _parse_status_arg(" , , ")


def test_audit_rejects_both_all_statuses_and_explicit_set(tmp_path):
    # PR #5 r3216119666: library-level mutual exclusivity. Without this,
    # all_statuses was silently ignored whenever a statuses set was given.
    (tmp_path / "specs").mkdir()
    with pytest.raises(ValueError, match="all_statuses=True and an explicit"):
        audit(root=tmp_path, all_statuses=True, statuses={"complete"})


def test_audit_cli_rejects_both_flags(tmp_path, capsys):
    # PR #5 r3216119652: CLI surfaces the conflict as a usage error via
    # argparse's mutually-exclusive-group machinery (exit code 2).
    (tmp_path / "specs").mkdir()
    with pytest.raises(SystemExit) as exc_info:
        main(["audit", "--root", str(tmp_path), "--all-statuses", "--status", "complete"])
    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "not allowed with" in captured.err or "argument" in captured.err


def test_all_statuses_constant_includes_n_a():
    # PR #5 r3214892213: docstring previously omitted n-a. The constant is
    # now the source of truth referenced by both audit and the CLI; pin it.
    assert "n-a" in ALL_STATUSES
    assert "unknown" in ALL_STATUSES


def test_audit_command_rejects_unknown_status_with_exit_code_2(capsys):
    rc = main(["audit", "--status", "nonsense", "--root", "."])
    captured = capsys.readouterr()
    assert rc == 2
    assert "unknown status" in captured.err


def test_audit_command_rejects_file_root_with_exit_code_2(tmp_path, capsys):
    f = tmp_path / "not-a-dir"
    f.write_text("hi", encoding="utf-8")
    rc = main(["audit", "--root", str(f)])
    captured = capsys.readouterr()
    assert rc == 2
    assert "not a directory" in captured.err


def test_lint_command_rejects_file_root_with_exit_code_2(tmp_path, capsys):
    f = tmp_path / "not-a-dir"
    f.write_text("hi", encoding="utf-8")
    rc = main(["lint", "--root", str(f)])
    captured = capsys.readouterr()
    assert rc == 2
    assert "not a directory" in captured.err
