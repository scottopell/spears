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

### Optional: Claude Code Agents

```bash
cp -r path/to/spears/.claude/agents .claude/
```

- `spears-update-markdown` - Updates spEARS specification files (requirements.md,
  design.md, executive.md) following EARS format and document separation rules
- `spears-validate-spec` - Validates specifications for structural correctness
  and cross-references codebase to verify status claims

### Optional: Claude Code Commands

```bash
cp -r path/to/spears/.claude/commands .claude/
```

- `/spears-reflection` - End-of-session command that reflects on progress,
  captures next steps, and outputs a continuation prompt to clipboard
