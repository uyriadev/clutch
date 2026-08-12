# prompts/ - reusable prompt fragments

Composable, stack-agnostic guidance you can drop into a `CLAUDE.md`, a system prompt,
or Cursor rules to raise the quality and consistency of AI output. Unlike `rules/`
(how to write a given *language*), these are about how the assistant *works and
communicates* on any task.

`setup.py` registers this project and `sync.py` shares the library through the global
store at `%USERPROFILE%\.clutch\prompts\`, so every project draws on the same set.

| File | Use it for |
|---|---|
| [code-craft.md](code-craft.md) | Making generated code specific, complete, and named precisely |
| [communication.md](communication.md) | Findings-first, filler-free responses calibrated to the task |
| [command-vocabulary.md](command-vocabulary.md) | A shared glossary so terse commands (fix/continue/optimize) mean one thing |
| [continuity.md](continuity.md) | Treating a session as one continuous project without losing the thread |
| [flowcharts.md](flowcharts.md) | Authoring flowcharts as Mermaid state diagrams + exporting high-res images |
| [human-output.md](human-output.md) | No AI tells: no co-author trailers, standard-keyboard characters only, casual comments, defer creative calls, verify sources, keep info.md |

## Metadata: every file declares what it is

Each file in `prompts/` and `guides/` opens with frontmatter, same convention as
`solutions/`:

```yaml
---
title: Communication - findings first, filler never
tags: [response-style, findings-first, filler, brevity, hedging]
modes: [core]
order: 20
---
```

`tags` are what keyword search matches on. `modes` decide when the file loads.
`scripts/library.py` reads it, `export.py` builds the AI.md mode table from it, and
the skills browser searches it - so nothing is maintained in two places.

```bash
python .clutch/scripts/library.py search encoding
```

## modes/ - work-phase playbooks

A mode is one phase of work: its procedure, its hard *never* list, and an exit
checklist that says what "done with this phase" means. Only the small routing table
ships in AI.md; the playbook itself loads when the phase starts.

| Mode | Enter when |
|---|---|
| [modes/plan.md](modes/plan.md) | 3+ files, a new component, or more than one plausible approach |
| [modes/code.md](modes/code.md) | the approach is settled and you are producing the edit |
| [modes/debug.md](modes/debug.md) | something is broken and the cause is unknown |
| [modes/review.md](modes/review.md) | auditing a diff or a file for defects |
| [modes/wrap.md](modes/wrap.md) | task done, signing off, or context about to reset |

Files marked `modes: [core]` are already inlined in AI.md - a phase only ever names
what is *new*, so modes stay cheap.

## design/ - decision playbooks

Run-on-demand reasoning for structural choices. Only the trigger table
([design/README.md](design/README.md)) travels in AI.md bundles; the playbooks are
read when a trigger fires.

| File | Run it before |
|---|---|
| [design/data-structures.md](design/data-structures.md) | Committing to how data is stored, accessed, or moved |
| [design/function-design.md](design/function-design.md) | Writing or reshaping a signature other code will call |

Both end in a `templates/design-decision.md` record: the distilled conclusion, not
the scratch work.

## How to use

- **Whole-file:** paste a file into your project's `CLAUDE.md` / rules.
- **Composed:** concatenate the ones you want. They don't conflict.
- **As a checklist:** each ends with a short self-check the assistant can run before
  sending a response.

These are distilled from prompt-engineering craft, rewritten to be **model-neutral and
safety-preserving** - they improve *how* work is done, never *whether* a request should
be declined. Refusal judgment stays with the assistant's own policies.
