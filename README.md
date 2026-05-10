# spEARS

spEARS (Simple Project with EARS) is a requirements-driven methodology for
working with AI coding agents.
It provides explicit traceability from business requirements to tests to code
using a strict three-document pattern (requirements.md, design.md, executive.md)
and EARS (Easy Approach to Requirements Syntax) format.

## Install

```bash
npx skills add scottopell/spears
```

This installs the `spears` skill into your project’s `.agents/skills/`
directory.

## What It Does

The skill provides six workflows, selected automatically based on context:

| Workflow | When it triggers |
| --- | --- |
| **Discover** | New feature, vague idea, “I want to build X” |
| **Write Specs** | Creating or updating requirements, design, or executive docs |
| **Implement** | Building from existing specs |
| **Validate** | Checking spec accuracy against the codebase |
| **Lint** | Enforcing quality rules, fixing violations |
| **Reflect** | End-of-session continuation prompt |

Discovery is the default entry point when intent is unclear -- it uses Socratic
questioning to understand user needs before writing anything.

## The Three-Document System

Every feature gets a spec directory with three files:

```
specs/feature-name/
  requirements.md   # WHAT to build (EARS format, immutable IDs)
  design.md         # HOW to build it (architecture, trade-offs)
  executive.md      # WHERE we are (status, milestones, progress)
```

Each document has a different relationship with time:
- **requirements.md** is timeless (defines the ideal end state)
- **design.md** is slightly ahead of reality (describes the technical approach)
- **executive.md** is the temporal link (reflects current reality)

## Key Principles

- **Specs without traceable user journeys are hollow.** Every requirement must
  trace to a real user doing a real thing.
- **Self-containment.** Every doc must be understandable without external
  context. No “as before”, no “unlike the old approach.”
- **Design describes architecture, not schedule.** Phasing decisions ("start
  with X, add Y later") belong in executive.md.
- **Requirements describe the ideal end state.** No migration concerns, no
  backwards compatibility, no implementation technology.
- **YAGNI.** Only implement what’s in requirements.md.

## CLI

A small `spears` CLI ships alongside the skill for mechanical checks
against your spec directory. It is stdlib-only Python (no runtime
dependencies). Run it from your project root:

```bash
# audit -- catch ✅ Complete REQs that have no anchor in code
python -m spears audit

# lint -- check title quality, Rationale presence, table shape, transparency contract
python -m spears lint
```

Or use the shim in `bin/spears` if you've cloned this repo directly.

### `spears audit`

Reads every spec under `<root>/specs/`, joins requirements.md headings
with the executive.md status table, and reports REQ-ids whose status is
✅ Complete but whose REQ-id never appears in any file outside `specs/`.
Exit code is `1` if any such REQ is found, so the command can be wired
into CI.

```bash
python -m spears audit                 # default: complete-only
python -m spears audit --all-statuses  # widen for migration / audit work
python -m spears audit --status complete,in-progress
python -m spears audit --spec rate-limiting --spec auth
```

### `spears lint`

Runs four rules:

- **R1** REQ titles must read as user benefits, not features. Flags
  gerund leading words, all-caps tech tokens, and noun-phrase titles.
- **R2** Every REQ in requirements.md must have a `**Rationale:**` block.
- **R3** Every status-table row must match the header's column count.
- **R4** If executive.md has a `## Transparency Contract` section, every
  declared REQ must have a question and every question must reference a
  declared REQ. Skipped silently when the section is absent.

### Performance

The audit walks the project with `os.walk` and prunes noise directories
(`.git`, `node_modules`, `__pycache__`, `dist`, `build`, `venv`, ...) in
place. The v1 prototype this is based on runs in ~0.2s on the workload
it was built for.

### Tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

Tests are split into property-based (Hypothesis) tests pinning round-trip
and structural invariants for the parser, scanner, audit filter, and the
two structural lint rules; and example-based tests against fixture
projects in `tests/fixtures/`.

## Links

- [EARS Whitepaper (Rolls-Royce)](https://www.researchgate.net/publication/224079416_Easy_Approach_to_Requirements_Syntax_EARS)
- [skills.sh](https://skills.sh)
