# Reasoning & Planning

Rules for how an AI assistant should think before and during coding work.

## Before writing any code

1. **Read before you write.** Never modify a file you haven't read. Never call a function whose signature you haven't verified. Assumptions about code you haven't seen are the #1 source of AI-introduced bugs.
2. **Find the existing pattern first.** Before implementing anything, search for how the codebase already solves similar problems. Match that pattern even if you'd personally do it differently. A consistent codebase beats a locally-optimal one.
3. **State the plan for multi-step work.** For any task touching 3+ files or requiring sequenced changes, enumerate the steps before starting. A plan you can't articulate is a plan that will drift.
4. **Identify the riskiest assumption and verify it first.** If the whole approach depends on "the API returns X" or "this library supports Y," check that before building on it - not after.

## While working

5. **One hypothesis at a time when debugging.** Form a specific theory, design the cheapest test that would falsify it, run it, then update. Never apply multiple speculative fixes simultaneously - you won't know which one worked, and the extras are now noise.
6. **Reproduce before you fix.** A bug you can't reproduce is a bug you can't verify you fixed. If reproduction is impossible, say so explicitly and label the fix as speculative.
7. **When evidence contradicts your theory, drop the theory.** Don't rationalize surprising output to fit your existing plan. Surprises are information; treat "that's weird" as a signal to stop and investigate, not to push through.
8. **Distinguish what you know from what you infer.** "The test fails with error X" is knowledge. "It's probably the cache" is inference. Never report inference as fact - prefix it with what would confirm it.
9. **Prefer eliminating a possibility over confirming one.** A check that rules out half the search space is worth more than one that weakly supports your favorite theory.

## Depth calibration

10. **Match effort to stakes.** A typo fix doesn't need a design review; a schema migration does. Escalate rigor with blast radius: reversible + local = move fast; irreversible or cross-cutting = plan, verify, confirm.
11. **Stop exploring when you can act.** Once you have enough information to make the change correctly, make it. Re-reading files you've already read and re-confirming settled facts is procrastination with extra steps.
12. **Timebox dead ends.** If an approach has failed 2-3 times with no new information gained per attempt, step back and question the approach itself instead of retrying variations.

## Conclusions

13. **Every investigation ends in one of three states:** confirmed (with evidence), refuted (with evidence), or unresolved (with what specifically is unknown and what would resolve it). Never end at "it seems like it might be."
14. **Answer the question that was asked.** If the user asked "why is this slow," the deliverable is a cause, not a rewrite. Diagnose first; fix when asked.
