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

## Links

- [EARS Whitepaper (Rolls-Royce)](https://www.researchgate.net/publication/224079416_Easy_Approach_to_Requirements_Syntax_EARS)
- [skills.sh](https://skills.sh)
