"""Lint rules for spEARS spec quality.

Each rule maps to an explicit guidance in the SKILL. Rules are intentionally
conservative: they flag only patterns the SKILL has called out as anti-
patterns, not every possible style preference. False positives are worse
than false negatives -- a noisy linter trains people to ignore it.

Rules:
  R1  REQ-SC-003: REQ titles start with a user verb. Anti-pattern: gerund
      first word (``Caching``, ``Logging``), all-caps tech token
      (``IP-Based``, ``JWT Token``), or noun-then-gerund (``Rate Limiting``).
  R2  REQ-SC-004: Every REQ in requirements.md has a Rationale block.
  R3  REQ-SC-005: Every status-table row has the same column count as the
      header.
  R4  REQ-SC-006: If executive.md has a "Transparency Contract" section,
      every question maps to a declared REQ id, and every declared REQ id
      appears in at least one question. Section is optional; the rule
      no-ops if absent.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from spears.parser import (
    REQ_ID_RE,
    Spec,
    StatusTable,
    discover_specs,
)

GERUND_RE = re.compile(r"[A-Za-z]{2,}ing$")
TECH_TOKEN_RE = re.compile(r"^[A-Z]{2,}(-|$)")  # ``IP``, ``JWT-``, ``API-``
TRANSPARENCY_HEADING_RE = re.compile(
    r"^#{2,}\s+Transparency\s+(Contract|Contracts|Questions)\b", re.IGNORECASE
)
ANY_HEADING_RE = re.compile(r"^#{1,6}\s")

# A small allowlist of imperative verbs the SKILL examples favour. The list
# is short by design: anything not on it falls through to the generic
# anti-pattern check (gerund / tech-token), which is what the v1 lesson
# actually catches. Treat the allowlist as a fast-path "definitely fine".
USER_VERBS: frozenset[str] = frozenset(
    {
        "Accept", "Access", "Add", "Allow", "Approve", "Audit", "Authenticate",
        "Authorize", "Avoid", "Block", "Browse", "Build", "Cancel", "Catch",
        "Change", "Check", "Choose", "Clear", "Compare", "Configure", "Confirm",
        "Copy", "Create", "Customize", "Decline", "Delete", "Deploy", "Describe",
        "Detect", "Diagnose", "Disable", "Discard", "Discover", "Display",
        "Distinguish", "Download", "Edit", "Enable", "Ensure", "Evaluate",
        "Explain", "Export", "Fetch", "Filter", "Find", "Generate", "Get",
        "Group", "Hide", "Identify", "Implement", "Import", "Inform", "Inspect",
        "Integrate", "Issue", "Learn", "Limit", "Lint", "List", "Log", "Maintain",
        "Manage", "Measure", "Migrate", "Modify", "Monitor", "Move", "Notify",
        "Optimize", "Organize", "Pause", "Personalize", "Pick", "Plan", "Prevent",
        "Provide", "Pull", "Push", "Read", "Receive", "Recover", "Reduce",
        "Reject", "Remove", "Rename", "Resume", "Restart", "Restore", "Restrict",
        "Retrieve", "Retry", "Reveal", "Review", "Save", "Schedule", "Search",
        "See", "Select", "Send", "Share", "Show", "Sign", "Sort", "Start", "Stop",
        "Submit", "Test", "Throttle", "Toggle", "Track", "Trace", "Understand",
        "Undo", "Update", "Upload", "Use", "Validate", "Verify", "View", "Warn",
    }
)


@dataclass
class LintIssue:
    rule: str  # e.g. "R1"
    spec: str
    file: Path
    line: int
    req_id: str | None
    message: str


@dataclass
class LintResult:
    issues: list[LintIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.issues


def _strip_token(word: str) -> str:
    return word.strip("*_`\"'.,:;")


def _check_title_verb(title: str) -> str | None:
    """Return an error message if the title violates R1, else None.

    The check is layered: if the first word is on the verb allowlist, the
    title is fine. Otherwise we look for two anti-patterns the SKILL has
    explicitly called out -- gerund first word and tech-token first word --
    and a third (noun-phrase pattern: ``<noun> <gerund>`` like ``Rate
    Limiting``). Anything else passes silently.
    """
    if not title.strip():
        return "title is empty"
    words = [_strip_token(w) for w in title.split()]
    words = [w for w in words if w]
    if not words:
        return "title starts with punctuation"
    first = words[0]
    if first in USER_VERBS:
        return None
    if TECH_TOKEN_RE.match(first):
        return f"title starts with tech token {first!r}; lead with a user verb"
    if GERUND_RE.match(first):
        return (
            f"title starts with gerund {first!r}; "
            f"rewrite as a user-action imperative"
        )
    if len(words) >= 2 and GERUND_RE.match(words[1]):
        return (
            f"title reads as a noun phrase ({first!r} + gerund {words[1]!r}); "
            f"lead with a user verb"
        )
    return None


def lint_titles(spec: Spec) -> list[LintIssue]:
    issues: list[LintIssue] = []
    for r in spec.requirements:
        msg = _check_title_verb(r.title)
        if msg:
            issues.append(
                LintIssue(
                    rule="R1",
                    spec=spec.name,
                    file=r.file,
                    line=r.line,
                    req_id=r.req_id,
                    message=msg,
                )
            )
    return issues


def lint_rationales(spec: Spec) -> list[LintIssue]:
    issues: list[LintIssue] = []
    for r in spec.requirements:
        if not r.rationale_present:
            issues.append(
                LintIssue(
                    rule="R2",
                    spec=spec.name,
                    file=r.file,
                    line=r.line,
                    req_id=r.req_id,
                    message="missing **Rationale:** block",
                )
            )
    return issues


def lint_status_table_shape(spec: Spec) -> list[LintIssue]:
    issues: list[LintIssue] = []
    table: StatusTable | None = spec.status_table
    if table is None:
        return issues
    expected = table.column_count
    for row in table.rows:
        if row.column_count != expected:
            issues.append(
                LintIssue(
                    rule="R3",
                    spec=spec.name,
                    file=row.file,
                    line=row.line,
                    req_id=row.req_id,
                    message=(
                        f"status row has {row.column_count} columns, "
                        f"header has {expected}"
                    ),
                )
            )
    return issues


def lint_transparency_contract(spec: Spec) -> list[LintIssue]:
    """R4: optional. Skips silently when no transparency section exists."""
    issues: list[LintIssue] = []
    if spec.executive_file is None:
        return issues
    text = spec.executive_file.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    section_start: int | None = None
    section_end: int | None = None
    for idx, line in enumerate(lines, start=1):
        if section_start is None and TRANSPARENCY_HEADING_RE.match(line):
            section_start = idx
            continue
        if section_start is not None and ANY_HEADING_RE.match(line):
            # Stop at the next heading of any level.
            section_end = idx
            break
    if section_start is None:
        return issues
    if section_end is None:
        section_end = len(lines) + 1
    section_lines = lines[section_start:section_end - 1]
    referenced: set[str] = set()
    for line in section_lines:
        for m in REQ_ID_RE.finditer(line):
            referenced.add(m.group(0))
    declared = spec.declared_ids
    missing = sorted(declared - referenced)
    extra = sorted(referenced - declared)
    for req in missing:
        issues.append(
            LintIssue(
                rule="R4",
                spec=spec.name,
                file=spec.executive_file,
                line=section_start,
                req_id=req,
                message=f"{req} declared but not covered in Transparency Contract",
            )
        )
    for req in extra:
        issues.append(
            LintIssue(
                rule="R4",
                spec=spec.name,
                file=spec.executive_file,
                line=section_start,
                req_id=req,
                message=(
                    f"Transparency Contract references {req} which is not "
                    f"declared in this spec"
                ),
            )
        )
    return issues


def lint_spec(spec: Spec) -> list[LintIssue]:
    issues: list[LintIssue] = []
    issues.extend(lint_titles(spec))
    issues.extend(lint_rationales(spec))
    issues.extend(lint_status_table_shape(spec))
    issues.extend(lint_transparency_contract(spec))
    return issues


def lint(root: Path, spec_filter: list[str] | None = None) -> LintResult:
    specs = discover_specs(root)
    if spec_filter:
        wanted = set(spec_filter)
        specs = [s for s in specs if s.name in wanted]
    result = LintResult()
    for spec in specs:
        result.issues.extend(lint_spec(spec))
    return result


def format_report(result: LintResult, root: Path) -> str:
    if not result.issues:
        return "No lint issues.\n"
    lines: list[str] = []
    by_spec: dict[str, list[LintIssue]] = {}
    for i in result.issues:
        by_spec.setdefault(i.spec, []).append(i)
    for spec, issues in sorted(by_spec.items()):
        lines.append(f"spec: {spec}")
        for issue in issues:
            try:
                rel = issue.file.resolve().relative_to(root.resolve())
            except ValueError:
                rel = issue.file
            req = f" {issue.req_id}" if issue.req_id else ""
            lines.append(
                f"  [{issue.rule}]{req} {rel}:{issue.line}: {issue.message}"
            )
        lines.append("")
    n = len(result.issues)
    plural = "s" if n != 1 else ""
    lines.append(f"Found {n} lint issue{plural}.")
    return "\n".join(lines).rstrip() + "\n"
