---
title: CONTEXT.md - keeping the window clean without losing accuracy
tags: [checkpoint, compaction, working-memory, reset, drift]
modes: [core]
order: 70
---

# CONTEXT.md - keeping the window clean without losing accuracy

`rules/ai/context-efficiency.md` covers how to *explore* economically. This guide
covers the other half: how to **deliberately shed context** on a long task while
keeping accuracy - by maintaining a compact, external working memory so the model
can be reset or compacted without amnesia.

The core idea: **context is lossy and biased (see `AI-PITFALLS.md`), so the source
of truth for a task should live in a file, not the window.** A fresh agent that
reads a good checkpoint outperforms a stale agent carrying 200 turns of drift.

## The working-memory checkpoint

`scripts/checkpoint.py` maintains one file - `checkpoint/current.md` - the live
state of the task in progress (template: `templates/checkpoint.md`). It holds only
what's load-bearing:

- **Goal** - the task in one or two sentences. What "done" means.
- **Constraints** - the rules that must survive drift (don't touch X, must stay
  backward-compatible, target Python 3.9). These are what long sessions forget first.
- **Decisions** - choices made and *why*, so they aren't relitigated or reversed.
- **Verified facts** - things actually checked this session (versions, file
  locations, test results), with where they came from. Marked verified, not assumed.
- **Open threads** - what's unfinished, what's next, what's blocked.
- **Do-not** - dead ends already tried, so a fresh context doesn't repeat them.

It is **not** a log (that's `history/`) and not a diary. If a line wouldn't matter
to someone picking up the task cold, it doesn't belong.

## When to checkpoint

- **Before a context reset or compaction** - so nothing load-bearing is only in the
  window. This is the whole point.
- **At milestones** - a sub-task done, a decision made, a fact verified. Update the
  relevant section immediately, while it's cheap and correct.
- **Before spawning a subagent** - hand it the checkpoint as its briefing (neutrally
  worded - see the anchoring warning in `AI-PITFALLS.md`).
- **When you notice drift** - if you're unsure whether a constraint still holds,
  stop and reconcile with the checkpoint rather than guessing.

## When to clear context (and why it helps accuracy)

Clearing isn't just about token cost - a bloated window *degrades* accuracy via
anchoring, lost-in-the-middle, and instruction drift. Reset when:

- The window is full of dead ends, back-and-forth, or resolved sub-problems.
- You've been anchored - going in circles on one framing.
- A distinct new phase begins (exploration done -> implementation; feature -> review).

**Procedure:** update `checkpoint/current.md` -> archive it if closing a phase
(`checkpoint.py archive`) -> reset -> the fresh context's first act is to read the
checkpoint. Accuracy is retained because the facts were externalized, not because
they were remembered.

## Checkpoint vs. the other stores

| Store | Holds | Lifetime |
|---|---|---|
| `checkpoint/current.md` | live task state (this guide) | until task done, then archived |
| `history/` | what happened per push | permanent, append-only |
| `solutions/` | reusable cross-project recipes | permanent, global |

Promote *out* of the checkpoint as work settles: a finished session's story ->
`history/` notes; a reusable discovery -> a `solutions/` file. The checkpoint stays
small because settled knowledge leaves it.

## For AI agents

On resuming a task, read `checkpoint/current.md` **first** - before re-exploring.
Keep it current as you work: the moment you verify a fact or make a decision, write
it there. Before any context reset, ensure the checkpoint alone is enough to
continue. When you finish the task, archive it and fold anything durable into
`history/` or `solutions/`.
