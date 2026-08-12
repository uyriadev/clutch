---
title: Plan mode - decide the approach before touching code
tags: [planning, approach, scope, risk, alternatives, checkpoint]
modes: [plan]
order: 10
---

# Plan mode - decide the approach before touching code

**Enter when** the task touches 3+ files, adds a component, changes a data shape or a
public signature, or has more than one plausible approach. Skip for a typo or a
one-line fix - depth matches stakes.

**Already loaded** (re-apply, don't re-read): `rules/ai/reasoning.md`,
`rules/ai/scope-control.md`, `prompts/design/README.md`.

**Load now** only if a structural choice is in play: the matching playbook from
`prompts/design/` per its trigger table.

## Procedure

1. **State the goal and what "done" means** in one or two sentences. If you cannot,
   you do not have the task yet - ask one specific question.
2. **Find the existing pattern first.** Search how this codebase already solves the
   nearest equivalent. Matching it beats a locally-better foreign design.
3. **Name the riskiest assumption and verify it now.** The one the whole approach
   rests on - "the API returns X", "this library supports Y". Check it before
   building on it, not after.
4. **Force a second approach.** Anchoring on the first plausible plan is the default
   failure. Name the alternative and say in one line why the chosen one wins.
5. **Enumerate the steps**, each with the files it touches. A plan you cannot
   articulate is a plan that will drift.
6. **Write `checkpoint/current.md`** - goal, constraints, decisions, verified facts.
   Constraints are what long sessions forget first.

## Never

- Start editing while in plan mode. The output of planning is a plan.
- Present a plan whose riskiest assumption is still unverified.
- Design a new pattern next to an existing one that already fits.
- Pad the plan with steps that exist to look thorough.

## Exit when

- [ ] `checkpoint/current.md` holds the goal, constraints, and step list.
- [ ] The riskiest assumption is verified, with the evidence named.
- [ ] A real alternative was considered and rejected for a stated reason.
- [ ] Each step names the files it touches.

Then switch to **code mode**.
