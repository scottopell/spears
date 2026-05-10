# Rate Limiting Design

## REQ-RL-001: Token bucket

Token bucket per (client_id, endpoint) tuple, refill at 100 tokens/min.

## REQ-RL-002: Quota endpoint

GET /quota returns the current bucket state for the calling client.

## REQ-RL-003: Cache layer

In-process LRU keyed by request signature.
