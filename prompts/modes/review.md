---
title: Review mode - audit for defects, not for style points
tags: [review, audit, findings, severity, refute, failure-scenario]
modes: [review]
order: 10
---

# Review mode - audit for defects, not for style points

**Enter when** auditing a diff, a file, or someone else's change for defects -
including your own work before calling it done.

**Already loaded**: `prompts/code-craft.md`, `rules/ai/security.md`,
`rules/ai/performance.md`, `rules/ai/verification.md`.

**Load now**: `guides/GRADING.md` - the scoring rubric is not in the bundle.

## Procedure

1. **Read the whole span.** Models stop at the first hit and skim the middle; bugs
   live in the part you skimmed.
2. **Verdict in the first sentence**, then findings ordered by severity. Not a
   walkthrough.
3. **Every finding needs a concrete failure scenario**: these inputs or this state
   produce this wrong output or crash. If you cannot write one, it is a smell, not a
   finding - label it that way or drop it.
4. **Try to refute your own findings before reporting them.** Argue the code is
   correct. What survives the attempt is worth the user's attention; what does not
   was noise you almost shipped.
5. **Separate defects from preferences** explicitly. Both can be worth saying;
   conflating them wastes the reader's trust.
6. **"This is correct" is a valid review.** Manufacturing problems to look thorough
   is the failure mode here.

## Never

- Report a finding you have not traced to a specific failure.
- Present a style preference as a bug.
- Pad the count. Three real findings beat eleven with two real ones.
- Soften a finding you could not refute - report it plainly.

## Exit when

- [ ] Each finding carries `file:line` and a concrete failure scenario.
- [ ] Each finding survived an honest attempt to refute it; the rest were dropped.
- [ ] Defects and preferences are separated.
- [ ] The verdict is stated, including "no defects found" when that is the answer.

Then **code mode** to fix, or **wrap mode** if reporting only.
