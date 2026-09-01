---
role: agent-instruction
scope: gc-policy
---

# GC Policy

## Short-term memory

Target: `_harness/memory/agents/*.local.md`

Rules:

- remove completed or obsolete working notes
- keep only active task context
- merge repeated notes into a short summary when useful
- do not commit local agent memory

## Long-term memory

Target: `_harness/memory/project.md`

Rules:

- keep durable decisions, conventions, and lessons
- remove outdated, superseded, or trivial notes
- merge duplicates
- rewrite for clarity when the same idea appears multiple times

## Harness content

Targets:

- `_harness/RULES.md`
- `_harness/WORKFLOW.md`
- `_harness/CATALOG.md`

Rules:

- remove dead or duplicated guidance
- keep rules short and high-signal
- move repeated project knowledge into memory when appropriate
