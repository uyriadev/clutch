---
title: Debug mode - find the cause before changing anything
tags: [debugging, hypothesis, reproduce, root-cause, falsify, solutions]
modes: [debug]
order: 10
---

# Debug mode - find the cause before changing anything

**Enter when** something is broken and you do not know why. If you already know the
cause, you are in code mode - go fix it.

**Already loaded**: `rules/ai/reasoning.md` (hypothesis discipline),
`rules/ai/verification.md`, `guides/SOLUTIONS.md`.

**Do this first, before anything else:** grep `solutions/` for the error text. The
answer to an environmental problem - encoding, paths, tool versions, OS quirks - is
often already written down. This is the highest-value step in the whole toolkit and
the most frequently skipped.

## Procedure

1. **Reproduce it.** A bug you cannot reproduce is a bug you cannot verify you
   fixed. If reproduction is genuinely impossible, say so and label every fix
   speculative.
2. **Grep `solutions/`** for the exact error string. Then grep the codebase for it.
3. **Read the whole error.** All of the stack trace, not the last frame. The
   bottom line is usually where it surfaced, not where it went wrong.
4. **One hypothesis at a time.** Write it down as a falsifiable claim, then design
   the *cheapest test that would prove it wrong*. Run that.
5. **Prefer eliminating half the search space** over confirming your favourite
   theory. A check that rules things out is worth more than one that weakly agrees.
6. **When evidence contradicts the theory, drop the theory.** Do not rationalize a
   surprise into your existing plan. "That's weird" means stop and look, not push on.
7. **Two or three failed attempts with no new information means the approach is
   wrong**, not the execution. Step back and question the framing. Consider a
   clean-context subagent given only the symptoms.
8. **Fix the cause, not the symptom.** A retry around a race is not a fix.
9. **Re-run the reproduction.** It must now fail to reproduce.

## Never

- Apply several speculative fixes at once - you will not know which worked, and the
  rest are now noise in the codebase.
- Wrap the failure in a `try`/`except` that hides it.
- Claim a fix works without re-running the thing that failed.
- End with "should be fixed" or "that should do it".

## Exit when

- [ ] The root cause is stated as a **mechanism** - not "a race condition" but which
      two operations raced, on what state, in what order.
- [ ] The original reproduction was re-run and no longer reproduces.
- [ ] The fix addresses the cause; symptom-level guards are named as such.
- [ ] If the cause was environmental, reusable, and cost real effort - a
      `solutions/<slug>.md` file is written. Without being asked.

Then **wrap mode**.
