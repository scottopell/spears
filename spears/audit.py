"""Status-aware unanchored detector.

A spec ``lies about implementation`` when executive.md claims a REQ is
``Complete`` but the codebase contains no anchor (no mention of the REQ-id
outside ``specs/``). That is the genuine subset worth surfacing by default;
verbose mode lifts the status filter and lists everything declared but
unanchored, which is noisier and used for migration / audit work.

REQ-SC-001: Catch Specs That Lie About Implementation
REQ-SC-002: View The Full Unanchored Set On Demand (--all-statuses)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from spears.parser import Spec, discover_specs
from spears.scanner import Mention, find_mentions, is_anchor_path


@dataclass
class AuditFinding:
    spec: str
    req_id: str
    title: str
    status: str  # complete | in-progress | ...
    declared_at: list[tuple[Path, int]]  # (file, line)


@dataclass
class AuditResult:
    findings: list[AuditFinding] = field(default_factory=list)
    parse_errors: list[tuple[str, str]] = field(default_factory=list)  # (spec, msg)

    @property
    def ok(self) -> bool:
        return not self.findings and not self.parse_errors


def _declaration_sites(spec: Spec, req_id: str) -> list[tuple[Path, int]]:
    sites: list[tuple[Path, int]] = []
    for r in spec.requirements:
        if r.req_id == req_id:
            sites.append((r.file, r.line))
    if spec.status_table:
        for row in spec.status_table.rows:
            if row.req_id == req_id:
                sites.append((row.file, row.line))
    return sites


def audit(
    root: Path,
    spec_filter: list[str] | None = None,
    all_statuses: bool = False,
    statuses: set[str] | None = None,
) -> AuditResult:
    """Audit specs under ``root`` for unanchored declarations.

    Parameters
    ----------
    root:
        Project root. Specs live in ``<root>/specs/``.
    spec_filter:
        If given, only audit specs whose directory name is in this list.
    all_statuses:
        If True, report every declared REQ that is unanchored, regardless of
        status. Equivalent to passing ``statuses={complete, in-progress,
        planned, not-started, manual, unknown}``.
    statuses:
        Explicit status filter. Defaults to ``{"complete"}`` -- the genuine
        ``spec lies about implementation`` subset.
    """
    if statuses is None:
        statuses = (
            {"complete", "in-progress", "planned", "not-started", "manual", "unknown"}
            if all_statuses
            else {"complete"}
        )

    specs = discover_specs(root)
    if spec_filter:
        wanted = set(spec_filter)
        specs = [s for s in specs if s.name in wanted]

    mentions = find_mentions(root)
    result = AuditResult()

    for spec in specs:
        for err in spec.parse_errors:
            # Missing executive.md is a hard problem for status-aware audit;
            # surface it but don't abort the whole run.
            result.parse_errors.append((spec.name, err))

        # Build a status map from executive.md. REQs declared only in
        # requirements.md (no status row) get status "unknown".
        status_map: dict[str, tuple[str, str]] = {}  # req -> (status, title)
        if spec.status_table:
            for row in spec.status_table.rows:
                status_map[row.req_id] = (row.status, row.title)
        for r in spec.requirements:
            status_map.setdefault(r.req_id, ("unknown", r.title))

        for req_id, (status, title) in status_map.items():
            if status not in statuses:
                continue
            anchors = [
                m for m in mentions.get(req_id, []) if is_anchor_path(m.path, root)
            ]
            if anchors:
                continue
            result.findings.append(
                AuditFinding(
                    spec=spec.name,
                    req_id=req_id,
                    title=title,
                    status=status,
                    declared_at=_declaration_sites(spec, req_id),
                )
            )
    return result


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

STATUS_LABEL = {
    "complete": "Complete",
    "in-progress": "In Progress",
    "planned": "Planned",
    "not-started": "Not Started",
    "manual": "Manual Verification",
    "n-a": "N/A",
    "unknown": "Unknown",
}


def format_report(result: AuditResult, root: Path) -> str:
    lines: list[str] = []
    if result.parse_errors:
        lines.append("Parse warnings:")
        for spec, msg in result.parse_errors:
            lines.append(f"  - [{spec}] {msg}")
        lines.append("")

    if not result.findings:
        lines.append("All targeted REQ declarations have anchors in code.")
        return "\n".join(lines).rstrip() + "\n"

    by_spec: dict[str, list[AuditFinding]] = {}
    for f in result.findings:
        by_spec.setdefault(f.spec, []).append(f)

    for spec, findings in sorted(by_spec.items()):
        lines.append(f"spec: {spec}")
        for f in findings:
            label = STATUS_LABEL.get(f.status, f.status)
            lines.append(
                f"  ✗ {f.req_id} ({f.title}): claimed {label} "
                f"but no anchor outside specs/"
            )
            for path, lineno in f.declared_at:
                try:
                    rel = path.resolve().relative_to(root.resolve())
                except ValueError:
                    rel = path
                lines.append(f"      declared at {rel}:{lineno}")
        lines.append("")

    n = len(result.findings)
    plural = "s" if n != 1 else ""
    lines.append(f"Found {n} unanchored declaration{plural}.")
    return "\n".join(lines).rstrip() + "\n"
