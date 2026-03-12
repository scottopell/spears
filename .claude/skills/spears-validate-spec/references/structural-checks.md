# Structural Linting Rules

## requirements.md

- [ ] Uses EARS format (WHEN/WHILE/WHERE/IF + THE SYSTEM SHALL)
- [ ] Has immutable IDs: REQ-[ABBREV]-###
- [ ] NO status fields (status belongs in executive.md)
- [ ] NO implementation details (belongs in design.md)
- [ ] Titles describe USER BENEFITS, not system features
- [ ] Rationale answers "Why does the USER care?"

## design.md

- [ ] All content traces to a REQ-* in requirements.md
- [ ] NO requirement definitions (belongs in requirements.md)
- [ ] NO status tracking (belongs in executive.md)
- [ ] NO "Future Considerations" or "Phase 2" sections
- [ ] Self-contained (no "as before", "improved", "previously" without
  specifics)

## executive.md

- [ ] ZERO code blocks (triple backticks) - inline backticks are fine
- [ ] 250 words max per summary section
- [ ] Status table includes requirement titles
- [ ] Uses valid status symbols: ✅ 🔄 ⏭️ ❌ ⚠️ N/A
- [ ] Progress count is accurate
