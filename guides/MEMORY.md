---
title: MEMORY.md - how to save and read memories
tags: [memory, checkpoint, history, solutions, stores]
modes: [core]
order: 72
---

# MEMORY.md - how to save and read memories

`.clutch` has three memory stores, each with a different lifetime and scope. This
guide is the usage reference: what each one is for, how to **save** to it, and how to
**read** from it. The bundle (`AI.md`) embeds a short version of this so an agent has
the memory API in the one file it caches.

| Store | Scope | Lifetime | Save with | Read with |
|---|---|---|---|---|
| **Working memory** - `checkpoint/current.md` | this task | until task done | `checkpoint.py new` + edit | `checkpoint.py show` |
| **Episodic** - `history/YYYY-MM-DD.md` | this project | permanent, append-only | pre-push hook / `history.py` | read newest file |
| **Long-term** - `solutions/*.md` | all projects | permanent, global | copy `templates/solution.md` | grep + `solutions/INDEX.md` |

Rule of thumb: **working** = what I'm doing right now, **episodic** = what happened,
**long-term** = a reusable lesson worth carrying to other projects. Promote outward as
knowledge settles: a finished task's story -> episodic; a reusable recipe -> long-term.

## Working memory (checkpoint)

The live state of the current task, so context can be reset without amnesia
(see `CONTEXT.md`).

```bash
python .clutch/scripts/checkpoint.py new "refactor the auth layer"   # start
python .clutch/scripts/checkpoint.py show                            # read it
python .clutch/scripts/checkpoint.py path                            # get path to edit
python .clutch/scripts/checkpoint.py archive                         # file it away, clear
```

**Save:** run `new`, then edit `checkpoint/current.md` directly (or via `path`) as you
work - the moment you verify a fact or make a decision, write it there.
**Read:** `show`, or just read `checkpoint/current.md`. On resuming a task, read this
**first**, before re-exploring.

## Episodic memory (history)

An append-only log of what changed each session, per project.

**Save:** happens automatically on `git push` (the pre-push hook runs `history.py`), or
run `python .clutch/scripts/history.py` by hand. Then replace the `<!-- notes -->`
placeholder in the new entry with why the change was made (see `HISTORY.md`).
**Read:** open the newest file in `history/` for recent context; older files for the
project's arc. `sync.py` also pushes these to `%USERPROFILE%\.clutch\history\<project>\`.

## Long-term memory (solutions)

Cross-project recipes - the memories that outlive one project (see `SOLUTIONS.md` for
what qualifies).

**Save:**
```bash
cp .clutch/templates/solution.md .clutch/solutions/<slug>.md   # then fill it in
python .clutch/sync.py                                            # publish globally
```
Fill in the frontmatter (`title`, `tags`, `projects`, `date`) and the
Problem / Root cause / Solution / Notes sections.

**Read:**
```bash
grep -ril "the exact error text" .clutch/solutions/    # search before debugging
```
or scan `solutions/INDEX.md` (auto-generated table of every solution across all
projects). Before debugging anything environmental (encoding, paths, tool versions),
read here first - the fix may already exist.

## For AI agents - the memory loop

1. **On start:** read working memory (`checkpoint/current.md`), skim `solutions/INDEX.md`,
   glance at the newest `history/` entry. The bundle `AI.md` already contains all three,
   so reading it covers this.
2. **While working:** keep the checkpoint current; grep `solutions/` before environmental
   debugging.
3. **On finish:** archive the checkpoint, write history notes, and if you solved something
   reusable, save a solution and run `sync.py`. Then regenerate the bundle with
   `python .clutch/export.py` so the next session's `AI.md` reflects the new memory.
