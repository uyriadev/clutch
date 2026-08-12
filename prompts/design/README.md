---
title: design/ - decision playbooks
tags: [design, trigger-table, decisions]
modes: [core]
order: 60
---

# design/ - decision playbooks

Step-by-step reasoning to run BEFORE writing code that commits to a shape: how data
is stored, how a function presents itself to callers. Unlike the sibling prompt
fragments (always-on style) and `rules/` (per-stack), these load on demand - only
this trigger table travels in the AI.md bundle. When a trigger fires, read the full
playbook from `.clutch/prompts/design/` if present, else from the global store at
`%USERPROFILE%\.clutch\prompts\design\`.

## Triggers

| Before you... | Read |
|---|---|
| Commit to how data is stored, accessed, or moved - a new collection, cache, index, queue, or a persisted / wire shape | `prompts/design/data-structures.md` |
| Write or reshape a function, method, or endpoint other code will call - params, return shape, errors, sync vs async, split vs keep | `prompts/design/function-design.md` |

Record the outcome with `templates/design-decision.md` - the distilled conclusion,
not the scratch work - wherever the project keeps design notes (docs, module
docstring, or the PR description).

## When NOT to run these

Depth must match stakes (see `rules/ai/reasoning.md`, depth calibration). Skip the
playbook when:

- The codebase already has a pattern for this exact job - match it and move on.
- The data is small, local, and short-lived (a handful of items inside one function).
- The function is private, has one caller, and its shape is obvious.

Run it when the choice is expensive to reverse, sits on a hot path, crosses a module
or API boundary, or will be persisted or sent over the wire.
