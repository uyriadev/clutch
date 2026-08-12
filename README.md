# .clutch

**New here? Start with [`guide.md`](guide.md)** - the operator's guide: a five-minute
setup path, how to confirm the rules are actually active, how to steer the five work
modes, and example prompts by task. This README covers the internals, and
[`ARCHITECTURE.md`](ARCHITECTURE.md) diagrams them - how a session moves through modes,
what ships in the bundle versus what waits on disk, the three retrieval paths, and how
a change propagates.

A guide-driven toolkit that lives inside each of your projects (as `.clutch/`) and
improves AI-assisted development over time:

1. **Commit grading** - `scripts/grade.py` takes commits and auto-generates a grading
   prompt (rubric included) that you feed to an AI to audit the code.
2. **Session history** - `scripts/history.py` runs after every push and writes a
   per-project markdown log of what changed that session into `history/`.
3. **Cross-project solutions** - when you solve a problem in a *general* way, log it in
   `solutions/` following `guides/SOLUTIONS.md`. `sync.py` merges these across all your
   projects into one global index.
4. **AI self-awareness** - `guides/AI-PITFALLS.md` names the LLM-specific failure modes
   (anchoring, sycophancy, confabulation...) and their countermeasures.
5. **Context hygiene** - `scripts/checkpoint.py` keeps an external working-memory file
   so context can be reset/compacted without losing accuracy (`guides/CONTEXT.md`).
6. **Stack code-rules** - `scripts/rules.py` assembles language/framework rules from the
   `rules/` library into one `RULES.md`, so AI-written code reads as human-written and
   matches the project's conventions.
7. **Reusable prompts** - the `prompts/` library holds composable, model-neutral prompt
   fragments (code craft, communication, command vocabulary, continuity) to drop into a
   `CLAUDE.md` or system prompt.
8. **Work modes** - `prompts/modes/` holds one playbook per phase (plan / code / debug /
   review / wrap): its procedure, its hard *never* list, and an exit checklist. Only a
   small routing table ships in the bundle; the playbook loads when the phase starts.
   `scripts/library.py` reads the `tags:`/`modes:` frontmatter that drives it, and also
   answers `library.py search <keyword>` when you want to find a prompt by hand.
9. **One-file bundle** - `export.py` dumps everything the AI needs (pitfalls, memory API,
   this project's stack rules, prompts, solutions index, recent history, current
   checkpoint) into a single `AI.md` the assistant reads once and caches - instead of
   opening a dozen files. A managed block in the project's `CLAUDE.md` points at it.
10. **Setup / sync** - `setup.py` registers the project, seeds the global store, and builds
   the bundle; `sync.py` keeps things in step with `%USERPROFILE%\.clutch` (same place
   as `.claude`). Libraries live **once** in the global store: a `consumer` project reads
   them from there (never copies the markdown in), a `source` install owns and syncs them.

## Docs

| Read | For |
|---|---|
| **[guide.md](guide.md)** | **Start here.** Five-minute setup, how to steer the five work modes, example prompts by task, troubleshooting. |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Diagrams: session flow, what ships in the bundle vs what waits on disk, retrieval paths, propagation. |
| [SKILLS-BROWSER.md](SKILLS-BROWSER.md) | The local web UI for browsing and staging prompts. |
| this README | Internals: layout, install, the daily workflow table. |

## Layout

```
.clutch/
├── README.md              this file
├── config.json            project name + settings
├── install_global.py      register the `clutch init` command (run once, source repo)
├── update_all.py          propagate latest toolkit + rebuild every project's bundle (`clutch update`)
├── install_project.py     what `clutch init` runs: consumer install into the cwd
├── setup.py               register project + seed global store + build bundle (run once)
├── export.py              dump everything into one cached AI.md (+ CLAUDE.md pointer)
├── sync.py                sync with %USERPROFILE%\.clutch
├── guides/
│   ├── AI-PITFALLS.md     AI-specific failure modes + how to counter them (read first)
│   ├── CONTEXT.md         keeping the context window clean without losing accuracy
│   ├── MEMORY.md          how to save & read the three memory stores
│   ├── MAINTAINING.md     the rule: run `clutch update` after every toolkit change
│   ├── GRADING.md         the rubric used to grade commits
│   ├── HISTORY.md         how session history entries are written
│   └── SOLUTIONS.md       what counts as a "general solution" and how to log it
├── templates/
│   ├── info.md            two-tier project overview scaffolded at each project root
│   ├── checkpoint.md      working-memory template used by checkpoint.py
│   ├── grading-prompt.md  template filled in by grade.py
│   ├── history-entry.md   template used by history.py
│   └── solution.md        template for new solution files
├── scripts/
│   ├── grade.py           commits -> grading prompt
│   ├── history.py         push -> session history entry
│   ├── checkpoint.py      working-memory checkpoint (clear context safely)
│   ├── rules.py           assemble stack code-rules -> RULES.md
│   ├── library.py         prompt/guide metadata: modes, tags, keyword search
│   ├── mermaid_export.py  render Mermaid diagrams to high-res SVG/PNG
│   ├── session_report.py  extract what a Claude session did from the .claude transcript
│   ├── transcript_commit.py  commit the session's work in transcript order, grouped by request
│   ├── ascii_normalize.py  replace non-keyboard characters with ASCII
│   ├── configure.py       interactive menu: pick which components go into AI.md
│   ├── tui.py             stdlib checkbox-menu widget used by configure.py
│   └── install_hooks.py   installs the git pre-push hook that runs history.py
├── rules/                 code-rules library (languages/frameworks/...); source-only, global is canonical
├── prompts/               reusable prompt fragments (+ modes/ phase playbooks, design/ decision playbooks); source-only, global is canonical
├── AI.md                  generated: the one-file bundle the AI reads (gitignored)
├── RULES.md               generated: this project's stack rules (gitignored)
├── checkpoint/            current.md (live task state) + archive/ (gitignored current)
├── grading/               generated grading prompts land here (gitignore if noisy)
├── history/               per-session change logs (YYYY-MM-DD.md)
└── solutions/
    ├── INDEX.md           auto-generated cross-project index (do not hand-edit)
    └── *.md               one file per solution
```

## Install into a project

**Fastest - the `clutch init` command.** Register it once (from this source repo):

```bash
python install_global.py
```

That publishes the toolkit to `%USERPROFILE%\.clutch\toolkit\`, drops launcher shims
in `%USERPROFILE%\.clutch\bin\`, and adds that dir to your user PATH. Then, in **any**
project folder, open a new terminal and run:

```bash
clutch init
```

It copies the toolkit into `./.clutch/`, **asks which components to bundle** (an
arrow-key menu - space toggles each guide/prompt/persona on or off, with a description of
each), writes a consumer `config.json`, and runs setup (seed global store, install the
pre-push hook, build `AI.md`). Re-running it in an existing project refreshes the toolkit
scripts without touching your config, solutions, history, or checkpoint. Re-run
`install_global.py` after changing toolkit scripts to republish.

Add `--defaults` to skip the menu (everything on). Reconfigure any time with:

```bash
python .clutch/scripts/configure.py
```

which shows the same menu and rebuilds `AI.md`. The choice persists in `config.json`
as `bundle_include` (+ the `operating_mode` flag).

**Manual alternative.** Copy this folder into the project root as `.clutch/`, then:

```bash
python .clutch/setup.py
```

`setup.py` creates the global store if needed, seeds it, runs the first sync, records
the project in `%USERPROFILE%\.clutch\projects.json`, installs the `pre-push` git
hook (so every push logs a session entry), and **builds `AI.md`** - the single file the
assistant reads. Pass `--no-hook` to skip the hook, `--inline` to embed the whole bundle
into `CLAUDE.md` instead of a pointer. Idempotent - safe to re-run.

### Consumer vs source

A **consumer** project (the normal case, `"role": "consumer"` - the default) needs only
`config.json`, `setup.py`, `sync.py`, `export.py`, and `scripts/` - **no** `guides/`,
`rules/`, `prompts/`, or `templates/` folders. Those libraries live once in the global
store; the scripts read them from there and `export.py` bakes the relevant parts into
`AI.md`. Nothing is copied per project.

The **source** install (this repo, `"role": "source"`) owns the libraries and syncs
them two-way with the global store. Run it once so the global store has content for
consumers to draw on.

### The one-file habit

The whole point: the assistant reads **`.clutch/AI.md`** once and caches it, instead
of opening pitfalls + context + rules + prompts + solutions separately. Re-run
`python .clutch/export.py` whenever `config.json` (stack), solutions, or the
checkpoint change, to refresh the bundle.

## Daily workflow

| When | Do |
|---|---|
| Reading in / picking up the project | read **`.clutch/AI.md`** (one file - pitfalls, memory, stack rules, prompts) |
| After a commit worth checking | `python .clutch/scripts/grade.py` (grades `HEAD`; pass a ref or range like `HEAD~3..HEAD`) - paste the generated prompt into your AI |
| On push | nothing - the hook writes `history/YYYY-MM-DD.md` |
| Need an accurate account of a session | `python .clutch/scripts/session_report.py` - extracts requests, files, commits, chapters from the `.claude` transcript (not guessed) -> `reports/`. Add `--history` to fill the newest history entry's notes |
| Ready to commit a session's work | `python .clutch/scripts/transcript_commit.py` (dry run) - groups changes by the request that produced them and plans commits in transcript order; add `--commit` to apply (`guides/COMMIT.md`) |
| Solved something reusable | save a memory: copy `templates/solution.md` into `solutions/`, fill it in (`guides/MEMORY.md`), then `sync.py` |
| Starting a non-trivial task | `python .clutch/scripts/checkpoint.py new "the task"` - working memory you can reset context around (`guides/CONTEXT.md`) |
| Entering a work phase | usually automatic - the AI picks the mode from the bundle's table. To drive it by hand: `python .clutch/scripts/library.py mode debug` and paste the read line |
| Hunting for the right prompt | `python .clutch/scripts/library.py search <keyword>` (matches tags, title, path), or run `python skills_browser.py` in the source repo for the clickable version |
| Setting up / changing the stack | set `stack` in `config.json`, then `python .clutch/export.py` to rebuild `AI.md` |
| After changing config / solutions / checkpoint | `python .clutch/export.py` - refresh the bundle |
| Project overview drifts from reality | update `info.md` at the project root (brief rundown + visuals/important bits, not code) |
| Start / end of a work session | `python .clutch/sync.py` |

## For the AI assistant working in a project

**Read `.clutch/AI.md` once, first - it's everything, cached in one file.** It bundles
the AI failure-mode checklist, the memory API, this project's stack code-rules, the prompt
guidance, the solutions index, recent history, and the current checkpoint. That single read
replaces opening `guides/`, `rules/`, `prompts/`, and `solutions/INDEX.md` one by one. The
project's `CLAUDE.md` has a managed block pointing you here.

From the bundle you'll know to:

- Run the **AI-PITFALLS** pre-flight before any non-trivial answer (anchoring, sycophancy,
  confabulation, premature closure; spawn a clean-context subagent for an unbiased second
  opinion when needed).
- Use the **memory API** (`guides/MEMORY.md`): read `checkpoint/current.md` first when
  resuming; save reusable fixes to `solutions/` and run `sync.py`; write history notes on push.
- **Follow the stack code-rules** embedded in the bundle - first commandment: *match what
  the project already does*, so AI-written code reads as human-written.

After changing config, solutions, or the checkpoint, run `python .clutch/export.py` to
refresh `AI.md`. When asked to review code, use the grading rubric (`guides/GRADING.md`).
