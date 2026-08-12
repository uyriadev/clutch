---
title: Wrap mode - persist what matters before the window closes
tags: [wrap-up, checkpoint, history, commit, propagation, handoff]
modes: [wrap]
order: 10
---

# Wrap mode - persist what matters before the window closes

**Enter when** the task is done, the user is signing off, the session is being
summarized, or context is about to reset or compact.

**Trigger phrases** - any of these means enter this mode now, without asking:
"wrap up", "wrap mode", "we're done", "that's it for today", "save state",
"save the session", "index this", "write it down", "commit this", "before I go".

**Already loaded**: `guides/CONTEXT.md`, `guides/MEMORY.md`, `guides/SOLUTIONS.md`,
`guides/HISTORY.md`, `guides/COMMIT.md`, `guides/MAINTAINING.md`.

The whole point: **nothing load-bearing may exist only in the context window.**
Context is lossy. Files are not.

## Procedure - the three stores, then publish

Work them in order. Each store has an owner script; writing the file is only half
the job, because the index that makes it findable is regenerated separately.

**1. Working memory - `checkpoint/current.md`**

Sweep the window first: what did you verify, decide, or rule out that is written
nowhere else? Put it in the checkpoint - facts under verified, dead ends under
do-not. Then:

```bash
python .clutch/scripts/checkpoint.py archive   # task finished
```

Task still open? Skip the archive, but leave the checkpoint good enough that a cold
reader could resume without asking a question.

**2. Conversation index - `history/`**

The pre-push hook writes an entry on `git push`, and *only* on push. No push means
no entry, so write it yourself:

```bash
python .clutch/scripts/session_report.py --history
```

That extracts the real requests, files, and commits from the `.claude` transcript
rather than reconstructing them from memory - which is the point, since your memory
of the session is the least reliable record of it.

**3. Solutions index - `solutions/` + `INDEX.md`**

Solve anything environmental, reusable past this repo, that cost real effort? Copy
`templates/solution.md` to `solutions/<specific-slug>.md`, fill in the frontmatter
(`title`, `tags`, `projects`, `date`), and say so. Do not wait to be asked. Then
publish - **the file alone does nothing until sync regenerates the index**:

```bash
python .clutch/sync.py
```

That merges solutions across every project and rebuilds `solutions/INDEX.md` from
frontmatter. Never hand-edit the index.

**4. Commit, if committing.** Group changes by the request that produced them and
commit in transcript order (`guides/COMMIT.md`, `scripts/transcript_commit.py`).

**5. Propagate, if the toolkit or libraries changed.** `clutch update`. Nothing
propagates on its own; an unpropagated change is not finished.

**6. Refresh the bundle.** Any of the above changed config, solutions, or the
checkpoint, so `AI.md` is now stale:

```bash
python .clutch/export.py
```

**7. Report honestly.** What is verified, what is assumed, what is still open. If
tests failed, say so with the output. If a step was skipped, say that.

## Never

- End on "should work" or "that should do it".
- Leave a hard-won discovery in the transcript only.
- Write a solution file and stop - unpublished, it is invisible to every project
  including this one.
- Reconstruct the session from memory when `session_report.py` can read the
  transcript.
- Claim done on something you did not run.
- Skip propagation because the change felt small.

## Exit when

- [ ] A fresh agent reading `checkpoint/current.md` could resume with no questions.
- [ ] The session has a `history/` entry - from the push hook or written by hand.
- [ ] Durable discoveries are in `solutions/` **and** `sync.py` has regenerated the
      index, so other projects can actually see them.
- [ ] Propagation ran if the toolkit or libraries changed.
- [ ] `export.py` re-ran, so `AI.md` reflects the new checkpoint and solutions.
- [ ] The final report separates verified from assumed and names what is open.
