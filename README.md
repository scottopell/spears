# spEARS

- [Methodology](SPEARS.md)
- [Agent Rules](SPEARS_AGENT.md)

## Claude Code Commands

spEARS includes reusable Claude Code slash commands in `.claude/commands/`.

### Available Commands

- `/spears-reflection` - End-of-session command that reflects on progress, captures next steps, and outputs a continuation prompt to clipboard

### Installation

**Option 1: Vendor into your project (recommended)**

Copy the `.claude/commands/` directory into your project's `.claude/` directory:

```bash
# From your project root
cp -r path/to/spears/.claude/commands .claude/
```

Commands become available to your whole team via git.

**Option 2: Personal installation**

Copy to your user commands directory for availability across all projects:

```bash
cp -r path/to/spears/.claude/commands/* ~/.claude/commands/
```

**Option 3: Plugin Marketplace (future)**

Claude Code supports a plugin marketplace system for versioned, auto-updating distribution. See [Plugin Marketplaces documentation](https://docs.anthropic.com/en/docs/claude-code/plugins#plugin-marketplaces) for details on creating a marketplace. This is a potential future direction for spEARS distribution.
