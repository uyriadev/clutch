---
title: SOLUTIONS.md - logging general solutions for cross-project reuse
tags: [solutions, cross-project, recipe, environmental, grep, reuse]
modes: [core]
order: 74
---

# SOLUTIONS.md - logging general solutions for cross-project reuse

`solutions/` is the project's slice of a global, cross-project library. `sync.py`
merges every project's solutions into `%USERPROFILE%\.clutch\solutions\` and
regenerates `INDEX.md`, then pulls the merged set back down - so every project sees
every solution.

## What qualifies as a "general solution"

Log it when **all three** hold:

1. **It cost real effort** - debugging, research, or several failed attempts.
   (If it was obvious, it doesn't need a file.)
2. **It generalizes** - the fix isn't specific to this project's code. It's about a
   tool, library, OS, protocol, or pattern that will recur elsewhere.
   - Good: "PowerShell 5.1 `Set-Content` writes ANSI unless `-Encoding utf8`"
   - Good: "SQLite `database is locked` under WAL: retry pattern that works"
   - Bad: "Renamed `UserSvc` to `AccountSvc` in this repo"
3. **It's stated as a recipe** - problem -> root cause -> fix, reproducible without
   this session's context.

## How to log one

1. Copy `templates/solution.md` into `solutions/<kebab-case-slug>.md`.
2. Fill in the frontmatter - `title`, `tags`, `projects`, `date`. Tags are how
   future searches find it; use tool/tech names (`python`, `git`, `windows`,
   `sqlite`), not vague words (`bug`, `fix`).
3. Body sections:
   - **Problem** - symptoms, exact error messages (verbatim - they're search keys).
   - **Root cause** - one paragraph, the actual mechanism.
   - **Solution** - the recipe. Runnable commands / paste-able code preferred.
   - **Notes** - caveats, versions it applies to, links.
4. Run `python .clutch/sync.py` to publish it globally.

## Rules

- One problem per file. Two related problems = two files with cross-links.
- Never hand-edit `INDEX.md`; it is regenerated from frontmatter on every sync.
- If you hit a problem an existing solution covers but the recipe was wrong or
  incomplete, **update the existing file** (and bump its `date`) instead of
  writing a duplicate.
- To delete a solution, delete it in **both** the project and the global store -
  the sync is union-based and will otherwise resurrect it on the next run.
- Filenames are global across all projects - make slugs specific
  (`powershell-utf8-set-content.md`, not `encoding-fix.md`).

## For AI agents

Before debugging anything that smells environmental (encoding, paths, tool
versions, OS quirks), grep `solutions/` for the error message first. After solving
something that meets the bar above, write the solution file without being asked and
mention it in your summary.
