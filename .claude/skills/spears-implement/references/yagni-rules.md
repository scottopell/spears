# YAGNI Enforcement

## DO NOT implement

- Features not in requirements.md (even if they seem useful)
- "Future-proofing" abstractions not required by current requirements
- Extra configuration options beyond what requirements specify
- Additional error handling beyond what requirements specify

## RED FLAGS (stop and reconsider)

- "While I'm here, I'll also..."
- "It would be nice to also..."
- "For extensibility, let me add..."
- "In case we need it later..."

If you catch yourself thinking these, **STOP**. Check if a requirement
actually asks for it. If not, don't build it.
