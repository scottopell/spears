# spears CLI Requirements

The spears CLI is a developer tool that audits and lints spEARS spec
directories so that authors can trust the executive.md status table to
reflect what is actually built.

The user is a developer or tech lead working on a project that uses spEARS.
They run the CLI from a project root that contains a `specs/` directory.

* * *

### REQ-SC-001: Catch Specs That Lie About Implementation

WHEN a developer runs `spears audit` against a project root, THE SYSTEM
SHALL report every requirement whose executive.md status is ✅ Complete
but whose REQ-id appears in no file outside the `specs/` tree, and SHALL
exit non-zero when any such requirement is found.

**Rationale:** Authors and reviewers need a fast, mechanical answer to
"does the executive table tell the truth?" Without it, a Complete row is
worth no more than the writer's last commit's worth of attention; with
it, a clean run is real evidence that every claim is anchored.

* * *

### REQ-SC-002: View The Full Unanchored Set On Demand

WHEN a developer passes `--all-statuses` to `spears audit`, THE SYSTEM
SHALL report every declared requirement that has no anchor outside
`specs/`, regardless of its status.

**Rationale:** During a migration or codebase audit, the developer wants
the full picture, not just the lying subset. The default stays narrow so
that day-to-day runs surface only actionable findings.

* * *

### REQ-SC-003: Catch Titles That Read As Features Not Benefits

WHEN a developer runs `spears lint`, THE SYSTEM SHALL flag every
requirement whose title leads with a gerund, an all-caps tech token, or a
noun-then-gerund phrase, with a message naming the offending pattern.

**Rationale:** The user-benefit framing is the most-cited lesson from the
PRs that drove this CLI. A title like "Caching Strategy" looks fine until
you ask "what does the user get from this?" -- and then it has no answer.
Catching the pattern at lint time keeps the question in front of authors
before review.

* * *

### REQ-SC-004: Catch Requirements Missing Their Rationale

WHEN a developer runs `spears lint`, THE SYSTEM SHALL flag every
requirement defined in requirements.md that does not contain a
`**Rationale:**` block within its section.

**Rationale:** A requirement without a rationale is a hint of a hollow
requirement. Forcing the author to write down "why does the user care?"
is the single cheapest filter against busywork.

* * *

### REQ-SC-005: Catch Status Tables With Inconsistent Row Shape

WHEN a developer runs `spears lint`, THE SYSTEM SHALL flag every status
row in executive.md whose column count differs from the header row.

**Rationale:** Markdown silently renders mismatched-column tables, so a
five-cell row in a four-column table will look fine in the browser and
parse wrong everywhere else. A linter is the only place this fails fast.

* * *

### REQ-SC-006: Catch Drift Between Status Table And Transparency Contract

WHEN a developer runs `spears lint` on a spec whose executive.md contains
a "Transparency Contract" section, THE SYSTEM SHALL flag every declared
requirement that is not referenced by a contract question, and every
contract question whose REQ-id is not declared in the spec.

**Rationale:** The contract is a user-facing promise about what the
system will answer. If a declared requirement has no question, the user
has no way to discover it; if a question references an unknown REQ, the
contract is making promises the spec does not back.
