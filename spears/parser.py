"""Parse spEARS spec directories.

Two declaration patterns are canonical and nothing else:

  1. `### REQ-XX-NNN:` headings in requirements.md
  2. `| **REQ-XX-NNN:**` rows in executive.md status tables

Cross-references in prose (e.g. "see REQ-XX-001") are *mentions*, not
declarations. Treating prose mentions as declarations defeated the v1
prototype because it inflated the declared-set with REQs that were really
just discussed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# A REQ ID looks like REQ-AB-001 or REQ-RL-12. The abbreviation is letters,
# the number is digits. Hyphenated abbreviations (REQ-FOO-BAR-001) are not
# permitted -- the SKILL spec is unambiguous: REQ-[ABBREV]-###.
REQ_ID_RE = re.compile(r"REQ-[A-Z][A-Z0-9]*-\d+")

# Heading-style declaration in requirements.md.
REQ_HEADING_RE = re.compile(r"^###\s+(REQ-[A-Z][A-Z0-9]*-\d+)\s*:\s*(.*?)\s*$")

# Status-table row in executive.md. The first cell looks like:
#   | **REQ-XX-NNN:** Title here ...
# The cell may contain trailing whitespace; the bolding is required for the
# row to count as a declaration.
REQ_STATUS_ROW_RE = re.compile(
    r"^\s*\|\s*\*\*\s*(REQ-[A-Z][A-Z0-9]*-\d+)\s*:\s*\*\*\s*(.*)$"
)

RATIONALE_RE = re.compile(r"^\s*\*\*Rationale\s*:?\*\*", re.IGNORECASE)

STATUS_SYMBOLS = {
    "✅": "complete",
    "🔄": "in-progress",
    "⏭️": "planned",
    "⏭": "planned",
    "❌": "not-started",
    "⚠️": "manual",
    "⚠": "manual",
}
NA_TOKEN_RE = re.compile(r"\bN/?A\b", re.IGNORECASE)


@dataclass
class Requirement:
    """A REQ declared via a heading in requirements.md."""

    req_id: str
    title: str
    file: Path
    line: int  # 1-indexed
    body_lines: list[str] = field(default_factory=list)
    rationale_present: bool = False


@dataclass
class StatusRow:
    """A REQ row in the executive.md status table."""

    req_id: str
    title: str
    status_symbol: str  # raw symbol or "" if none recognised
    status: str  # normalised: complete | in-progress | planned | not-started | manual | n-a | unknown
    file: Path
    line: int  # 1-indexed
    column_count: int


@dataclass
class StatusTable:
    file: Path
    header_line: int
    column_count: int
    rows: list[StatusRow] = field(default_factory=list)


@dataclass
class Spec:
    """A parsed spec directory."""

    name: str
    path: Path
    requirements_file: Path | None = None
    design_file: Path | None = None
    executive_file: Path | None = None
    requirements: list[Requirement] = field(default_factory=list)
    status_table: StatusTable | None = None
    parse_errors: list[str] = field(default_factory=list)

    @property
    def declared_ids(self) -> set[str]:
        """Union of REQ IDs declared by either canonical pattern."""
        ids = {r.req_id for r in self.requirements}
        if self.status_table:
            ids.update(row.req_id for row in self.status_table.rows)
        return ids


def _split_table_row(line: str) -> list[str]:
    """Split a markdown table row into cells, dropping leading/trailing empties.

    A row like `| a | b | c |` yields ["a", "b", "c"].
    """
    stripped = line.strip()
    if not stripped.startswith("|"):
        return []
    parts = stripped.split("|")
    # First and last entries are empty if the row is well-formed.
    if parts and parts[0] == "":
        parts = parts[1:]
    if parts and parts[-1] == "":
        parts = parts[:-1]
    return [p.strip() for p in parts]


def _is_separator_row(cells: list[str]) -> bool:
    """A markdown table separator row: every cell is dashes (with optional colons)."""
    if not cells:
        return False
    return all(re.fullmatch(r":?-{2,}:?", c) for c in cells)


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def parse_requirements(path: Path) -> list[Requirement]:
    """Extract REQ headings from a requirements.md file."""
    lines = _read_lines(path)
    reqs: list[Requirement] = []
    current: Requirement | None = None
    for idx, line in enumerate(lines, start=1):
        m = REQ_HEADING_RE.match(line)
        if m:
            current = Requirement(
                req_id=m.group(1),
                title=m.group(2).strip(),
                file=path,
                line=idx,
            )
            reqs.append(current)
            continue
        # Stop accumulating when we hit a heading of equal-or-greater level.
        if current is not None and re.match(r"^#{1,3}\s", line):
            current = None
            continue
        if current is not None:
            current.body_lines.append(line)
            if RATIONALE_RE.match(line):
                current.rationale_present = True
    return reqs


def _classify_status(cell: str) -> tuple[str, str]:
    """Return (raw_symbol, normalised_status) for a status cell."""
    for sym, name in STATUS_SYMBOLS.items():
        if sym in cell:
            return sym, name
    if NA_TOKEN_RE.search(cell):
        return "N/A", "n-a"
    return "", "unknown"


def parse_status_table(path: Path) -> StatusTable | None:
    """Find the first status table in executive.md and parse REQ rows from it.

    A status table is identified as the first contiguous block of pipe-prefixed
    lines that contains at least one REQ row.
    """
    lines = _read_lines(path)
    in_table = False
    table_start = -1
    table_lines: list[tuple[int, list[str]]] = []
    for idx, line in enumerate(lines, start=1):
        is_pipe = line.lstrip().startswith("|")
        if is_pipe:
            cells = _split_table_row(line)
            if not in_table:
                in_table = True
                table_start = idx
                table_lines = []
            table_lines.append((idx, cells))
        else:
            if in_table:
                table = _build_status_table(path, table_start, table_lines)
                if table is not None:
                    return table
                in_table = False
                table_start = -1
                table_lines = []
    if in_table:
        return _build_status_table(path, table_start, table_lines)
    return None


def _build_status_table(
    path: Path, start_line: int, rows: list[tuple[int, list[str]]]
) -> StatusTable | None:
    if not rows:
        return None

    def _is_req_row(cells: list[str]) -> bool:
        if not cells:
            return False
        # Reconstruct enough of the row for the regex anchored at `|`.
        return REQ_STATUS_ROW_RE.match(f"| {cells[0]} |") is not None

    if not any(_is_req_row(cells) for _, cells in rows):
        return None
    # Header column count: first non-separator row.
    header_line = start_line
    column_count = len(rows[0][1])
    for line_no, cells in rows:
        if not _is_separator_row(cells):
            header_line = line_no
            column_count = len(cells)
            break
    table = StatusTable(file=path, header_line=header_line, column_count=column_count)
    for line_no, cells in rows:
        if _is_separator_row(cells):
            continue
        if not cells:
            continue
        first = cells[0]
        m = REQ_STATUS_ROW_RE.match(f"| {first} |")
        if not m:
            continue
        req_id = m.group(1)
        # Title: text after `**REQ-...:**` in the first cell.
        title = re.sub(
            r"^\*\*\s*REQ-[A-Z][A-Z0-9]*-\d+\s*:\s*\*\*\s*", "", first
        ).strip()
        # Status cell is conventionally the second column.
        status_cell = cells[1] if len(cells) > 1 else ""
        sym, status = _classify_status(status_cell)
        table.rows.append(
            StatusRow(
                req_id=req_id,
                title=title,
                status_symbol=sym,
                status=status,
                file=path,
                line=line_no,
                column_count=len(cells),
            )
        )
    return table


def parse_spec(spec_dir: Path) -> Spec:
    """Parse a spec directory: requirements.md + design.md + executive.md.

    Missing files are tolerated (recorded in parse_errors) so that linting can
    still report on what is present.
    """
    spec = Spec(name=spec_dir.name, path=spec_dir)
    req_file = spec_dir / "requirements.md"
    design_file = spec_dir / "design.md"
    exec_file = spec_dir / "executive.md"
    if req_file.is_file():
        spec.requirements_file = req_file
        spec.requirements = parse_requirements(req_file)
    else:
        spec.parse_errors.append(f"missing {req_file.name}")
    if design_file.is_file():
        spec.design_file = design_file
    else:
        spec.parse_errors.append(f"missing {design_file.name}")
    if exec_file.is_file():
        spec.executive_file = exec_file
        spec.status_table = parse_status_table(exec_file)
        if spec.status_table is None:
            spec.parse_errors.append(f"{exec_file.name} has no status table")
    else:
        spec.parse_errors.append(f"missing {exec_file.name}")
    return spec


def discover_specs(root: Path) -> list[Spec]:
    """Find spec directories under <root>/specs/ and parse each one."""
    specs_root = root / "specs"
    if not specs_root.is_dir():
        return []
    specs: list[Spec] = []
    for entry in sorted(specs_root.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue
        # A spec dir must have at least one of the three canonical files.
        if not any((entry / f).is_file() for f in ("requirements.md", "design.md", "executive.md")):
            continue
        specs.append(parse_spec(entry))
    return specs
