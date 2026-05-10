# Authentication Requirements

### REQ-UA-001: Sign In With Email

WHEN a user submits a valid email and password, THE SYSTEM SHALL issue a
session token that expires after 24 hours of inactivity.

**Rationale:** Returning users can resume their work without re-entering
credentials on every visit.

### REQ-UA-002: Block Repeated Failed Attempts

WHEN a user submits an invalid password five times in a row, THE SYSTEM
SHALL lock the account for 15 minutes.

**Rationale:** Account holders are protected from automated guessing
without permanent lockout.
