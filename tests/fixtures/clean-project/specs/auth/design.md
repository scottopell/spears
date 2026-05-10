# Authentication Design

## REQ-UA-001: Session token

HMAC-signed JWT with 24h sliding expiry; refreshed on each authenticated
request.

## REQ-UA-002: Lockout counter

Per-account counter in Redis with 15-minute TTL.
