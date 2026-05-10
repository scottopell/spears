# spears CLI Executive

## Status

| Requirement | Status | Anchors |
| --- | --- | --- |
| **REQ-SC-001:** Catch Specs That Lie About Implementation | ✅ Complete | `spears/audit.py`, `tests/test_audit_property.py`, `tests/test_examples.py` |
| **REQ-SC-002:** View The Full Unanchored Set On Demand | ✅ Complete | `spears/audit.py`, `spears/cli.py` |
| **REQ-SC-003:** Catch Titles That Read As Features Not Benefits | ✅ Complete | `spears/lint.py`, `tests/test_lint_examples.py` |
| **REQ-SC-004:** Catch Requirements Missing Their Rationale | ✅ Complete | `spears/lint.py`, `tests/test_lint_property.py` |
| **REQ-SC-005:** Catch Status Tables With Inconsistent Row Shape | ✅ Complete | `spears/lint.py`, `tests/test_lint_property.py` |
| **REQ-SC-006:** Catch Drift Between Status Table And Transparency Contract | ✅ Complete | `spears/lint.py`, `tests/test_transparency_contract.py` |

## Summary

V1 of the spears CLI ships with two commands -- `audit` and `lint` --
backed by a stdlib-only Python package. The audit command is the
status-aware unanchored detector that the v1 prototype proved out: it
filters to ✅ Complete by default so a clean run is meaningful in CI,
and widens to every status under `--all-statuses` for migration work.
The lint command runs four rules: user-verb titles, Rationale presence,
status-table column-shape consistency, and the optional Transparency
Contract 1:1 mapping.

The package is tested at two layers: Hypothesis property tests pin
round-trip and structural invariants for the parser, scanner, audit
filter logic, and the two purely structural lint rules; example-based
tests pin the message shape of audit/lint reports against hand-crafted
fixture projects (a "lying" project that exercises every failure mode
and a "clean" project that must pass every check).

## Out Of Scope For V1

A tree-sitter-backed grammar would unlock `spears query`, `spears diff`
against git history, and `spears anchors --status=complete`, and would
naturally subsume the stdlib parser. V1 deliberately defers it: the
canonical-declaration regexes are simple enough to maintain by hand and
fast enough to keep the audit under a second on real projects.

## Transparency Contract

- Q: Will my CI catch a Complete row whose REQ-id never appears in code?
  (REQ-SC-001)
- Q: Can I get the full list of unanchored REQs during a migration?
  (REQ-SC-002)
- Q: Will the linter tell me when a title reads as a feature instead of
  a benefit? (REQ-SC-003)
- Q: Will the linter tell me when a requirement is missing its
  rationale? (REQ-SC-004)
- Q: Will the linter notice a status row whose column count drifts away
  from the header? (REQ-SC-005)
- Q: Will the linter flag a Transparency Contract that no longer matches
  the declared requirements? (REQ-SC-006)
