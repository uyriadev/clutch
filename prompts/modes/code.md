---
title: Code mode - produce the change that was decided
tags: [implementation, editing, patterns, verification, scope]
modes: [code]
order: 10
---

# Code mode - produce the change that was decided

**Enter when** the approach is settled and you are producing the edit. If you are
still choosing the approach, that is plan mode. If you do not know why something is
broken, that is debug mode.

**Already loaded**: `prompts/code-craft.md`, `rules/ai/code-quality.md`,
`rules/ai/scope-control.md`, plus this project's stack rules (in the bundle under
*Code rules*). Re-apply them; do not re-read them.

## Procedure

1. **Read every file before you edit it.** Never modify a file you have not read;
   never call a function whose signature you have not verified. This is the single
   biggest source of AI-introduced bugs.
2. **Match the local convention** - naming, error handling, import style, test
   framework. Foreign-but-correct code is still a defect.
3. **Write complete code.** No stubs, no `TODO`, no `pass` bodies, no placeholder
   constants left for later. Real imports, real error handling.
4. **Only what was asked.** When you spot something else worth fixing, note it
   separately - do not fold it into this change.
5. **Verify by running it**, and quote the actual output. Not "this should work".
6. **Update the checkpoint at milestones** - a decision made, a fact verified, a
   sub-task done. While it is cheap and correct.

## Never

- Modify a file you have not read this session.
- Assert an identifier - flag, signature, version, config key - you have not seen.
- Weaken, skip, or delete a test to make a run go green.
- Refactor adjacent code you were not asked to touch.
- Report success you did not observe.

## Exit when

- [ ] The change is complete - nothing stubbed, nothing deferred silently.
- [ ] It ran, and the real output is quoted.
- [ ] Out-of-scope findings are listed separately, not silently fixed or dropped.
- [ ] `checkpoint/current.md` reflects the current state.

Then **review mode** if the change is substantial, otherwise **wrap mode**.
