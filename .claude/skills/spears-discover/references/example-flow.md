# Example Socratic Discovery Flow

This shows a typical discovery session for an API rate limiting feature.

## Opening

Agent explores codebase, finds no existing rate limiting specs.
Starts from Motivation level.

## Motivation

```text
Agent: "What problem are we solving? Who has this problem?"
User: "Users need to see their API usage stats."

Agent synthesizes: Usage visibility is the surface need.

Agent: "Why do they need to see them? What decision does this inform?"
User: "So they know if they're approaching limits."

Agent synthesizes: The real need is avoiding surprise throttling.
```

## Journey

```text
Agent: "What happens when they approach limits? Walk me through that moment."
User: "They get warned, then throttled if they exceed."

Agent synthesizes: This is the CRITICAL path. Probing business impact.
```

## Critical Path

```text
Agent: "If throttling surprises them, what's the business impact?"
  Options: ["Lost trust", "Churn", "Support tickets", "All of above"]
User: "Definitely churn. Our power users would leave."

Agent synthesizes: Critical journey = notice limit -> take action -> stay happy.

Agent: "What actions can they take to avoid throttling?"
  Options: ["Upgrade plan", "Reduce usage", "Request exception"]
```

## Convergence

The loop continues until the user confirms: "Yes, you've got it."
Only then does the agent produce the handoff document and invoke the
writing skill.
