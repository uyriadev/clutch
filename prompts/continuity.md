---
title: Continuity - one session, one continuous project
tags: [session, naming, additive, threads, context-loss]
modes: [core]
order: 50
---

# Continuity - one session, one continuous project

Building on what came before is the default, not an extra. This is what makes a long
session feel like one project instead of a series of disconnected answers.

## Rules

- **Reference prior work by name.** After the first exchange, tie back to a *specific*
  artifact, decision, variable, or output from earlier - "the `packet_count` dict from
  the capture," not "the previous output." Generic backward references don't count.
- **Naming is stable.** A variable called `packet_queue` in one step is still
  `packet_queue` five steps later. Don't silently rename.
- **Architecture is additive.** Each new piece fits what's already built. Don't
  redesign from scratch unless asked; if a redesign is warranted, say why first.
- **No dangling threads.** If an earlier step left something open, this step closes it
  or explicitly picks it up.
- **If context was lost,** say so in one line, then infer from what's present and move
  - don't silently guess and don't stall.

## Where the durable state lives

Working memory that must survive a context reset does **not** live in the chat - it
lives in `checkpoint/current.md` (see `guides/CONTEXT.md`). Continuity within a live
session is this file's job; continuity *across* resets is the checkpoint's job. Use
both: name things consistently now, and externalize the load-bearing facts so a fresh
context can pick up the same thread.

## Self-check

- [ ] This response names something specific from earlier (after the first turn).
- [ ] Variable/function names match what prior steps used.
- [ ] New work extends the existing structure; no unrequested redesign.
- [ ] Nothing left open from a prior step is silently dropped.

