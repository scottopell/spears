"""Examples for R4 (Transparency Contract 1:1 mapping).

R4 silently no-ops if the section is absent, so the absence test matters
as much as the presence tests.
"""

from __future__ import annotations

from pathlib import Path

from spears.lint import lint


def _setup(tmp_path: Path, exec_body: str) -> Path:
    spec = tmp_path / "specs" / "feat"
    spec.mkdir(parents=True)
    (spec / "requirements.md").write_text(
        "# Reqs\n\n"
        "### REQ-FE-001: View Status\n\n**Rationale:** Users care.\n\n"
        "### REQ-FE-002: Export History\n\n**Rationale:** Users care.\n",
        encoding="utf-8",
    )
    (spec / "design.md").write_text("# Design\n", encoding="utf-8")
    (spec / "executive.md").write_text(exec_body, encoding="utf-8")
    return tmp_path


def test_R4_silent_when_no_transparency_section(tmp_path):
    root = _setup(
        tmp_path,
        "# Exec\n\n## Status\n\n"
        "| Req | Status |\n| --- | --- |\n"
        "| **REQ-FE-001:** View Status | ✅ Complete |\n"
        "| **REQ-FE-002:** Export History | ✅ Complete |\n",
    )
    result = lint(root=root)
    assert not [i for i in result.issues if i.rule == "R4"]


def test_R4_flags_missing_req_in_section(tmp_path):
    root = _setup(
        tmp_path,
        "# Exec\n\n## Status\n\n"
        "| Req | Status |\n| --- | --- |\n"
        "| **REQ-FE-001:** View Status | ✅ Complete |\n"
        "| **REQ-FE-002:** Export History | ✅ Complete |\n\n"
        "## Transparency Contract\n\n"
        "- Q: How do I see my status? (REQ-FE-001)\n",
    )
    result = lint(root=root)
    r4 = [i for i in result.issues if i.rule == "R4"]
    assert any(i.req_id == "REQ-FE-002" and "not covered" in i.message for i in r4)


def test_R4_flags_extra_req_in_section(tmp_path):
    root = _setup(
        tmp_path,
        "# Exec\n\n## Status\n\n"
        "| Req | Status |\n| --- | --- |\n"
        "| **REQ-FE-001:** View Status | ✅ Complete |\n"
        "| **REQ-FE-002:** Export History | ✅ Complete |\n\n"
        "## Transparency Contract\n\n"
        "- Q: How do I see my status? (REQ-FE-001)\n"
        "- Q: How do I export? (REQ-FE-002)\n"
        "- Q: How do I delete? (REQ-FE-999)\n",
    )
    result = lint(root=root)
    r4 = [i for i in result.issues if i.rule == "R4"]
    assert any(
        i.req_id == "REQ-FE-999" and "not declared" in i.message for i in r4
    )
