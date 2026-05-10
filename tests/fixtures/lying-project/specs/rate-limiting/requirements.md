# Rate Limiting Requirements

### REQ-RL-001: Prevent Abuse Attacks

WHEN a client exceeds 100 requests per minute, THE SYSTEM SHALL refuse
further requests with a 429 response for 60 seconds.

**Rationale:** Users sharing the API don't get squeezed out by abusers
hammering the same endpoints.

### REQ-RL-002: View Current Quota

WHEN a client requests their quota status, THE SYSTEM SHALL return the
remaining requests and the reset time.

**Rationale:** Users can plan their work without guessing whether the next
call will fail.

### REQ-RL-003: Caching Strategy

WHILE the cache is warm, THE SYSTEM SHALL respond from cache.

This requirement intentionally violates R1 (gerund title) and is missing
its Rationale block.
