# Quality Checklist

Run on every change.

## User-Centricity (requirements.md)

- [ ] Title describes USER BENEFIT, not system feature
- [ ] WHEN clause describes user action/context
- [ ] SHALL clause describes observable user outcome
- [ ] Rationale explains why user cares

## Implementation-Creep Detection

- [ ] No data structure field names in requirements
- [ ] No algorithm/technology names in requirements
- [ ] No code-like language in requirements
- [ ] Implementation details only in design.md

## Self-Containment (ALL documents)

- [ ] No time-dependent references ("as before", "previously")
- [ ] No comparative language requiring prior knowledge
- [ ] Document understandable standalone

## Scope Check (design.md)

- [ ] Every section traces to a REQ-* in requirements.md
- [ ] No "Future Considerations" or "Phase 2" sections
- [ ] No speculative extensibility without corresponding requirements
- [ ] Content describes HOW to build defined requirements only

## BANNED PHRASES (rewrite immediately)

- "as before" / "as currently implemented" / "previously"
- "maintain existing behavior" / "continue to work as expected"
- "as it does today" / "unchanged from current behavior"
- "same as [other feature]" / "following the established pattern"
