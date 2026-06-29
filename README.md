# spEARS

spEARS (Simple Project with EARS) is a lightweight, requirements-first
specification methodology for building software with AI agents.
Its goal is a clear shared understanding of how a system should work — one that
stays honest as the code evolves.

It gets there by matching each kind of knowledge to a medium that fits it,
rather than forcing everything into one always-stale design document:

- **`requirements.md`** — timeless EARS requirements (the *what*, plus why a
  user cares), with immutable `REQ-IDs`.
- **`specs/adrs/`** — a shared chain of point-in-time Architecture Decision
  Records (the *why*, frozen at the moment each decision was made).
- **`*.allium`** — precise, checkable behavioral specs (the *how, exactly*),
  reached for only when a feature is complex enough to warrant it.
- **`executive.md`** — the one document that tracks the present: status, and
  forward-looking open questions.

The reasoning behind that split is the heart of the method — see
[`skills/spears/references/design-philosophy.md`](skills/spears/references/design-philosophy.md).

## Where it lives

spEARS is packaged as a skill.
The canonical entry point is [`skills/spears/SKILL.md`](skills/spears/SKILL.md)
— a lean hub that routes to references for EARS authoring, ADRs, discovery,
validation, traceability, and worked examples.
Point your agent at the skill (or install it as a skill in Cowork / Claude Code)
and it will pull in the rest as needed.

## Optional: Allium

[`skills/allium/`](skills/allium) is a vendored companion skill for the precise
behavioral layer. It is **optional** — spEARS is complete on its own.
Install Allium when you want formal behavioral specs and generated tests for the
complex minority of features that earn them.
