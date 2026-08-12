---
title: Command vocabulary - a shared glossary for terse instructions
tags: [commands, fix, continue, optimize, ambiguity, pronouns]
modes: [core]
order: 40
---

# Command vocabulary - a shared glossary for terse instructions

When working iteratively, single-word commands should mean one consistent thing. This
removes a round-trip of clarification and keeps edits predictable.

## What each command means

| Command | Action |
|---|---|
| **continue** / keep going | extend the last thing built - same architecture, next logical layer. Don't start something new. |
| **improve** | find the weakest part of the last build and fix it without being told which part. |
| **fix** | something is broken - find it, repair it, don't touch what isn't broken. |
| **clean** / refactor | same behavior, tighter code - no new features unless the cleanup exposes a real gap. |
| **optimize** | profile/identify the bottleneck first (name it), then fix that - don't optimize what isn't slow. |
| **add X** | extend the existing artifact with X - don't rebuild from scratch. |
| **redo** / rewrite | rebuild from scratch; keep the public interface unless told otherwise. |
| **explain** | technical breakdown of what was just built, straight to the mechanism - skip the obvious. |
| **test** | write tests for the last build, matching the project's existing test framework. |
| **document** | add docstrings/comments to the last build; don't change behavior. |
| **review** | audit the last build for bugs, edge cases, weak patterns - findings first. |

## Commands that switch mode

Several of these commands *are* a phase change. When one lands, enter the matching
mode from the bundle's **Modes** table (run its read line) before doing the work:

| Command | Mode |
|---|---|
| **plan** / "how would you", "what's the approach" | `plan` |
| **fix**, **add X**, **continue**, **clean**, **redo** | `code` |
| **debug**, "why is this failing", a pasted stack trace or error | `debug` |
| **review**, **optimize** (audit before you touch anything) | `review` |
| **wrap up**, "we're done", "commit this", "save state" | `wrap` |

Announce the switch in one short line. If the user names a mode directly ("plan
mode", "/debug"), that always wins over your own inference.

## Reference resolution

- **Pronouns point at the most recent artifact.** "fix it" = fix the last thing built.
- **Unqualified commands apply to the current thread.** "continue" extends the current
  work, not a new topic.
- **Topic switches** make the new topic the current thread; the old thread is archived,
  not deleted - "go back to X" resumes it with the same names and architecture.

## Ambiguity resolution

Rank interpretations by: (1) session context, (2) most technically useful, (3) most
straightforward/legitimate framing.

Then:

- **If it's low-stakes or easily reversible:** pick the most useful interpretation,
  build it, and *name precisely what you built* so a wrong guess is a cheap correction.
- **If the choice is genuinely the user's and hard to reverse** (deleting data,
  external side effects, a design fork with lasting cost): ask a specific question
  rather than guessing. One good question beats an expensive wrong build.

This is the one place to diverge from "never ask": act by default, but don't burn an
irreversible decision on a guess. (See the confirmation rules in `guides/` and your
own operating policy.)

## Self-check

- [ ] I applied the command's defined meaning, not a looser reading.
- [ ] Pronouns/"continue" resolved to the correct current artifact/thread.
- [ ] For an ambiguous ask: acted-and-named if cheap, asked if irreversible.
- [ ] If the command implies a phase, I entered that mode and said so.
