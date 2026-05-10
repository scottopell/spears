# spears CLI Design

The CLI is a stdlib-only Python package (`spears/`) exposed through
`python -m spears` and a `bin/spears` shim. Its three layers -- parser,
scanner, command -- map directly to the load-bearing design choice from
the v1 prototype: scan code broadly for REQ mentions, but treat specs
canonically.

## REQ-SC-001 / REQ-SC-002: Status-aware unanchored detection

The `audit` command joins three data sources:

1. **Declarations** (canonical): REQ-ids extracted from spec files using
   exactly two patterns -- `### REQ-XX-NNN:` headings in requirements.md
   and `| **REQ-XX-NNN:**` rows in executive.md status tables. Cross-
   references in prose are deliberately not declarations: treating them
   as such inflated the declared set with REQs that were merely discussed,
   which is the v1 mistake the prototype was built to fix.

2. **Status map** (executive.md): Each status row is parsed for its
   leading symbol (✅ 🔄 ⏭ ❌ ⚠ or "N/A") and normalised to a string
   (`complete`, `in-progress`, ...). REQs declared only in requirements.md
   get status `unknown`.

3. **Anchors** (broad): A `find_mentions` pass walks the project with
   `os.walk` and prunes noise dirs (`.git`, `node_modules`, `__pycache__`,
   `dist`, `build`, `target`, `venv`, ...) in place via
   `dirnames[:] = [...]`. Any REQ-id mention in any text file is recorded;
   anchors are the subset whose path is not under `specs/`.

A finding is a (REQ, status, declaration sites) triple where the REQ has
a status in the active filter set and the anchor list is empty. The
default filter is `{complete}` -- the genuine "spec lies about
implementation" set. `--all-statuses` widens the filter to every status,
producing the full unanchored set for migration / audit work.

The CLI exits non-zero whenever findings are non-empty, so the audit can
be wired into CI as a guard.

## REQ-SC-003, REQ-SC-004, REQ-SC-005, REQ-SC-006: Lint rules

Lint rules are independent functions (`lint_titles`, `lint_rationales`,
`lint_status_table_shape`, `lint_transparency_contract`) that each take a
parsed `Spec` and return a list of `LintIssue`. The `lint` command runs
all four against every spec.

### R1 (title heuristic, REQ-SC-003)

A layered check:

- If the first word is on a small allowlist of common user-action verbs,
  the title is fine.
- Else, if the first word ends in `-ing`, flag a gerund.
- Else, if the first word matches `^[A-Z]{2,}(-|$)`, flag a tech token
  prefix (`IP-Based`, `JWT Token`).
- Else, if the title's first two words are `<noun> <gerund>`, flag a
  noun-phrase title (`Rate Limiting`).
- Otherwise, pass silently.

The deliberate looseness is the point. False positives erode trust in
the linter; only the SKILL's explicit anti-patterns trigger a flag.

### R2 (rationale presence, REQ-SC-004)

Each REQ section in requirements.md spans from its `### REQ-...:` heading
to the next heading of level 1, 2, or 3 (`#`, `##`, or `###`). Subheadings
of level 4 or deeper (`####`, `#####`) stay inside the section, so authors
can sub-organise a REQ with `#### Acceptance Criteria` or similar without
ending it. A section satisfies R2 when at least one line within it matches
`^\s*\*\*Rationale\s*:?\*\*` (case-insensitive).

### R3 (status-table shape, REQ-SC-005)

The first non-separator row of the status table sets the column count.
Every other row must match. Pipe rows are split via a small helper that
strips the leading and trailing empty cells produced by `| a | b |`-style
markdown.

### R4 (transparency contract, REQ-SC-006)

The check looks for an `^#{2,}\s+Transparency (Contract|Contracts|
Questions)` heading in executive.md and parses the section between that
heading and the next heading at any level. The set of REQ-ids referenced
in the section is compared against the spec's declared-id set; the symmetric
difference produces flagged issues. If the section is absent, the rule
no-ops -- it only fires when an author has opted into the pattern.

## Performance

The hot path is the `find_mentions` walk. The single optimisation that
matters is in-place dirname pruning: a typical Node project's
`node_modules` contains tens of thousands of files, all of which would be
stat'd and re-opened without pruning. With pruning, the v1 prototype
runs in 0.2s on the workload it was built for.

## CLI surface

```
spears audit [--root PATH] [--spec NAME ...] [--all-statuses] [--status LIST]
spears lint  [--root PATH] [--spec NAME ...]
```

Both commands return:

- `0` if there are no findings/issues
- `1` if findings/issues exist
- `2` for usage errors (missing root, etc.)
