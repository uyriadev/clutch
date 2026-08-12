---
title: MAINTAINING.md - the propagation rule
tags: [propagation, sync, update, toolkit, publish]
modes: [core]
order: 80
---

# MAINTAINING.md - the propagation rule

Nothing in clutch propagates on its own. Each project keeps its own copy of the
scripts, and each bundle (`AI.md`) is a baked snapshot. So there is one standing rule.

## The rule

**After any change to the toolkit or the libraries, run `clutch update` before the
task is done.** It rebuilds every registered project's bundle so no project is left
stale.

```bash
clutch update            # or: python .clutch/update_all.py
```

"A change" means: a script in `scripts/`, a guide / prompt / rule / template, a config
default, the persona, or a new bundle component. If you touched any of those, propagate.

## What it does

`update_all.py` reads the registry (`%USERPROFILE%\.clutch\projects.json`) and:

1. From the source repo: `sync.py` (libraries -> global store) and `install_global.py`
   (scripts -> toolkit). This publishes your change.
2. For every consumer project: refreshes its scripts from the toolkit and rebuilds its
   `AI.md` (via `install_project.py --defaults`, which keeps each project's config).

It is idempotent - run it as often as you like. Preview with `--dry-run`.

## Why it is not fully automatic

There is no file-watcher or daemon; the trigger is you running the command (or an agent
running it as part of finishing a change). This keeps it simple and predictable. A git
hook on the source repo could call it on commit, but the source repo is not currently a
git repo - if it becomes one, add a `post-commit` hook that runs `clutch update`.

## Manual equivalent (if the command is unavailable)

```bash
python sync.py                       # libraries -> global
python install_global.py             # scripts -> toolkit (+ registers the command)
# then in each project:
clutch init --defaults           # refresh scripts + rebuild that bundle
```

## New projects

`clutch init` in a project registers it. From then on `clutch update` includes it
automatically - so onboarding a project is a one-time step, and updates reach it after.
