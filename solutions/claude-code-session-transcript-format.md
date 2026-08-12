---
title: Parsing Claude Code session transcripts (.claude JSONL) for reports
tags: [claude-code, jsonl, transcript, python, reports]
projects: [clutch]
date: 2026-08-01
---

## Problem

You want to generate an accurate account of what a Claude Code session did (requests,
files changed, commits) instead of having the model reconstruct it from memory. Where
is the data and how is it shaped?

## Root cause

Claude Code writes an append-only JSONL transcript per session, one JSON object per
line, under the user's config dir:

```
<CLAUDE_CONFIG_DIR or ~/.claude>/projects/<encoded-cwd>/<session-id>.jsonl
```

- **Encoded cwd:** the working directory with `:` `/` `\` all replaced by `-`
  (`C:\Users\me\Documents\code\proj` -> `C--Users-me-Documents-code-proj`). Key off the
  directory the command is *run from* (`Path.cwd()`), not a path derived from the
  script's own location.
- **Filename stem = the conversation/session id.**

## Solution

Event `type`s that matter: `user`, `assistant`, `custom-title`, `system`, plus metadata
(`queue-operation`, `mode`, `last-prompt`, `attachment`).

- **Genuine human prompts:** `type=="user"` AND `message.content` is a *string* AND
  `origin.kind == "human"` AND not `isMeta`. This is the reliable filter -
  `promptSource` is unreliable (seen as `null`/`sdk`), and tool-results also arrive as
  `user` events but with `content` as a *list* of `tool_result` blocks. Background task
  notifications are `origin.kind == "task-notification"`.
- **Tool calls:** `type=="assistant"`, `message.content` is a list; blocks with
  `type=="tool_use"` have `name` and `input`. Files -> `input.file_path` for
  `Edit/Write/MultiEdit/NotebookEdit`; commands -> `input.command` for `Bash/PowerShell`;
  chapters -> `mcp__ccd_session__mark_chapter` (`input.title`/`input.summary`).
- **Errors:** `tool_result` blocks with `is_error: true` (inside `user` events). Note a
  non-zero Bash exit is flagged as an error even when benign - label accordingly.
- **Title:** last `custom-title` event's `customTitle`. **Branch/cwd/timestamp:** present
  on most `user`/`assistant`/`system` events (`gitBranch`, `cwd`, `timestamp`).

Working implementation: `scripts/session_report.py`.

## Notes

- Reports contain `-> x ...`; on Windows `sys.stdout.reconfigure(encoding="utf-8",
  errors="replace")` before printing, or a piped/legacy-codepage run raises
  `UnicodeEncodeError`. Files should be written with `encoding="utf-8"`.
- Override the store with `CLAUDE_CONFIG_DIR`. Timestamps are UTC (`...Z`).
