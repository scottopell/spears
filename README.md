# spEARS

spEARS (Simple Project with EARS) is a lightweight methodology for working with AI coding agents. It provides structured prompts and rules that help agents understand project context, track progress, and maintain consistency across sessions. The approach emphasizes root cause analysis and reflection over quick fixes.

- [Methodology](SPEARS.md)
- [Agent Rules](SPEARS_AGENT.md)

## Installation

Copy `SPEARS.md` and `SPEARS_AGENT.md` into your project's root directory:

```bash
# From your project root
cp path/to/spears/SPEARS.md path/to/spears/SPEARS_AGENT.md .
```

Then reference them in your project's `CLAUDE.md` or `AGENTS.md`.

### Optional: Claude Code Commands

spEARS also includes reusable Claude Code slash commands in `.claude/commands/`. To use them, copy the commands directory:

```bash
# From your project root
cp -r path/to/spears/.claude/commands .claude/
```

Commands become available to your whole team via git.

#### Available Commands

- `/spears-reflection` - End-of-session command that reflects on progress, captures next steps, and outputs a continuation prompt to clipboard
