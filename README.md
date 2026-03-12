# spEARS

spEARS (Simple Project with EARS) is a lightweight methodology for working with
AI coding agents. It provides structured prompts and rules that help agents
understand project context, track progress, and maintain consistency across
sessions. The approach emphasizes root cause analysis and reflection over quick
fixes.

- [Methodology](SPEARS.md)
- [Agent Rules](SPEARS_AGENT.md)

## Installation

Copy `SPEARS.md` and `SPEARS_AGENT.md` into your project's root directory:

```bash
cp path/to/spears/SPEARS.md path/to/spears/SPEARS_AGENT.md .
```

Add a reference to them in your project's `CLAUDE.md` or `AGENTS.md`. I
recommend putting an @-reference to automatically include SPEARS_AGENT.md and
only referencing SPEARS.md for extra details.

### Optional: Claude Code Skills

Install globally (available in all projects):

```bash
cp -r path/to/spears/.claude/skills/* ~/.claude/skills/
```

Or install per-project:

```bash
cp -r path/to/spears/.claude/skills .claude/skills
```

Available skills:

- `/spears-discover` - Socratic discovery for new specs. Iterative questioning
  to establish motivation, personas, journeys, critical paths, and edge cases
  before writing.
- `/spears-reflection` - End-of-session reflection that captures progress,
  current state, and next steps as a continuation prompt.
- `/spears-update-markdown` - Updates spEARS specification files
  (requirements.md, design.md, executive.md) following EARS format and document
  separation rules.
- `/spears-validate-spec` - Validates specifications for structural correctness
  and cross-references codebase to verify status claims.
- `/spears-implement` - Implements requirements following design.md. Accepts
  requirement IDs or spec paths. Tracks status in executive.md.
