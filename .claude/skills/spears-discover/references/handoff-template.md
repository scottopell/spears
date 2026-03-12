# AI-to-AI Handoff Document Template

This is NOT for human consumption. Optimize for information density. No fluff.

```text
# Spec Discovery Handoff

## Target
specs/[feature-name]/

## Scope
[new-full | update-requirements | update-design | targeted]

## Motivation
[Dense prose: why this exists, business context, what failure means]

## Personas
[For each persona: name, role, distinguishing characteristics, goals]

## User Journeys
[For each journey: trigger -> steps -> expected outcome]
[Mark which requirements likely map to each journey]

## Critical Paths
[Journeys where failure = business damage]
[Why they're critical, what failure looks like]

## Edge Cases
[Known failure modes, unclear scenarios, decisions deferred]

## Unknowns
[What we explicitly chose not to resolve, and why]

## Cross-Spec Impact
[Other specs that may need updates based on these discoveries]
```
