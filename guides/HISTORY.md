---
title: HISTORY.md - how session history is written
tags: [history, session-notes, push, episodic]
modes: [core]
order: 76
---

# HISTORY.md - how session history is written

`scripts/history.py` runs on every push (via the pre-push hook) and appends an entry
to `history/YYYY-MM-DD.md` in this project's `.clutch`. `sync.py` then copies the
history up to the global store under `%USERPROFILE%\.clutch\history\<project>\`.

## Purpose

The history folder answers two questions months later:

1. **What actually happened in this project, session by session?** (for humans)
2. **What context does an AI need to pick this project back up?** (for agents)

## What an entry contains

Each push appends one entry (see `templates/history-entry.md`):

- **Timestamp + branch + commit range** - machine-recoverable anchor into git.
- **Commits** - subject lines of everything pushed.
- **Files touched** - diffstat summary.
- **Session notes** - free-text section. `history.py` leaves a placeholder;
  fill it in (or have the AI fill it in) with:
  - *why* the changes were made, not what (git already knows what),
  - decisions taken and alternatives rejected,
  - anything left broken or half-done,
  - candidate solutions that should be promoted to `solutions/` (link them).

## Rules

- One file per day, entries appended in order. Never rewrite past entries.
- Entries are per-project; cross-project knowledge goes in `solutions/`, not here.
- Keep notes in full sentences. A future reader has zero context from this session.
- If a push was trivial (typo, version bump), a one-line note is fine - but say so
  explicitly ("trivial: version bump only") rather than leaving the placeholder.

## For AI agents

At session start, read the most recent history file to recover context. At session
end (or after pushing), replace the `<!-- notes -->` placeholder in the newest entry
with real session notes following the rules above.
