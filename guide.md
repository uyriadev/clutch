# Using clutch - the operator's guide

**What this is:** a toolkit that lives in each project as `.clutch/`, feeds your AI
assistant one pre-assembled context file, and gets better over time because the AI
writes what it learns back into it.

**What you do:** install it, tell it your stack, then talk normally. Most of the
machinery is automatic. This guide covers the parts that are not.

For the rules themselves read `.clutch/AI.md`; for internals read `README.md`; for
diagrams of how it all fits, `ARCHITECTURE.md`.

---

## Start here - about five minutes

**1. Install into a project.** From the project folder:

```bash
clutch init
```

That registers the project, creates `.clutch/`, builds the bundle, and adds a
managed block to the project's `CLAUDE.md` pointing the assistant at it.

**2. Tell it your stack.** This is the one bit of config that matters, and nothing
auto-detects it. Edit `.clutch/config.json`:

```json
"stack": ["python", "fastapi", "postgresql", "pytest"]
```

Names match rule-file stems; `python .clutch/scripts/rules.py --list` shows every
valid name. The universal `ai/` rules are always included regardless.

**3. Rebuild and start a fresh session.**

```bash
python .clutch/export.py
```

**4. Confirm it loaded.** Ask the assistant anything real. You should get a header
like this before the answer:

```
⚙️ clutch engaged
prompts:
  prompts/operating-mode.md
  prompts/communication.md
  guides/AI-PITFALLS.md
```

That is your proof of life. See *Is it actually working* below.

---

## Is it actually working

Cheapest checks first:

- **The marker.** `⚙️ clutch engaged` on a substantive reply means the bundle loaded.
  No marker on real work usually means it did not - see Troubleshooting.
- **The prompts receipt.** The indented paths under the marker name every library file
  that shaped that answer. It should *change between answers*. An identical list every
  time means it is being written as boilerplate rather than earned - call that out.
- **Ask it to prove it:**
  > Are you in operating mode? List the bundle components loaded and the mode you are in.
- **Ask for verified-vs-assumed.** The rules require separating what was checked from
  what is guessed:
  > Redo that and mark what you verified vs assumed.

If you changed a rule, the stack, or config, run `export.py` and start a fresh session.

---

## How you steer it: the five modes

Work happens in phases. The assistant picks the phase itself from what you asked - but
**you can force one at any time, and your word always wins.** Just say it in plain
English; there is no special syntax.

| Say something like | Phase | What changes |
|---|---|---|
| "plan", "how would you", "what's the approach" | `plan` | Names the risky assumption and verifies it *first*, forces a second approach, writes a checkpoint. Will not start editing. |
| "fix", "add X", "continue", "implement" | `code` | Reads every file before editing it, matches local conventions, no stubs, runs the result and quotes real output. |
| "debug", "why is this failing", or paste an error | `debug` | Greps past solutions first, reproduces, then one falsifiable hypothesis at a time. No shotgun fixes. |
| "review", "audit", "check this" | `review` | Findings first by severity, each with a concrete failure scenario, self-refuted before you see it. |
| "wrap up", "save state", "index this", "before I go" | `wrap` | Persists all three memory stores, commits in transcript order, propagates. |

Naming the mode outright - "plan mode", "/debug" - overrides its inference. Use that
when it guessed wrong.

Each phase has an **exit checklist** it must satisfy before moving on, which is the
real value: `plan` cannot hand off to `code` with an unverified assumption, and `debug`
is not done until the root cause is stated as a mechanism and the reproduction stops
reproducing.

### Wrapping up properly

This is the one to build a habit around, because it is what makes the toolkit improve.
Say **"wrap up"** and it will work the three memory stores in order:

```bash
python .clutch/scripts/checkpoint.py archive        # 1. working memory
python .clutch/scripts/session_report.py --history  # 2. conversation index
python .clutch/sync.py                              # 3. solutions + INDEX
python .clutch/export.py                            # refresh the bundle
```

Note step 3: writing a solution file is only half the job. Until `sync.py` runs, the
index is not regenerated and no other project can see it.

---

## Finding the right guidance

The bundle carries a **Library map** - all ~114 tags and the file that covers each one.
The assistant reads the path straight from that table; no search needed. You can browse
the same index yourself:

```bash
python .clutch/scripts/library.py tags          # every tag -> its file
python .clutch/scripts/library.py search cache  # keyword -> ranked files
python .clutch/scripts/library.py modes         # the phases and their read lines
```

Each prints a ready-to-paste line: `Read <paths> in full for context.`

In the **source repo only**, `python skills_browser.py` opens a clickable version -
filter by tag, double-click a mode chip to stage its whole read line, copy it out.

To pull something in by hand mid-conversation:

> Read prompts/design/data-structures.md in full, then pick the structure for this.

---

## Example prompts by task

Single-word commands have defined meanings, so short prompts are safe and predictable.

**Building and changing**
- Feature: `Add <feature>. Follow the code-rules. If the shape of the project changes, update info.md.`
- Bug: `fix <symptom or error text>` - repairs only the broken thing
- Cleanup: `clean <file or area>` - same behavior, tighter code
- Extend: `continue` - next logical layer on what was just built
- Improve: `improve` - finds and fixes the weakest part unprompted
- Optimize: `optimize <area>` - names the bottleneck before touching it
- Rewrite: `redo <thing>, keep the interface`

**Design decisions** (these trigger the reasoning playbooks)
- `How should I store this?` - runs the data-structure playbook: operations first, then
  the constraint, then real candidates including the boring one
- `Design the signature for <function>` - runs the function-design playbook

**Understanding and reviewing**
- `explain <thing>` - straight to the mechanism
- `review` - findings first, each with a failure scenario
- `grade HEAD and act on the audit`, or run `python .clutch/scripts/grade.py`
- Unbiased second opinion: `spin up a clean-context subagent to check this, worded
  neutrally, and compare`

**Diagrams**
- `Make a flowchart of <process>.` - authored as a Mermaid state diagram
- `python .clutch/scripts/mermaid_export.py diagram.md --scale 4`

**Sessions and memory**
- `what did we do this session?` or `python .clutch/scripts/session_report.py`
- `log that as a solution` - writes `solutions/<slug>.md`, then sync
- `check solutions before debugging this`
- `checkpoint this task before we continue`

---

## How it gets better over time

Three stores, each with a different lifetime. This is the part new users miss, and it
is the whole reason the toolkit is worth using over a plain `CLAUDE.md`.

| Store | Holds | Lives |
|---|---|---|
| `checkpoint/current.md` | the task in progress - goal, constraints, verified facts, dead ends | until the task is done |
| `history/` | what changed each session | permanent, per project |
| `solutions/` | reusable fixes that generalize past this repo | permanent, **shared across every project** |

`solutions/` is the compounding one. Solve a Windows encoding quirk once, run `sync.py`,
and every project you own can find it by error text forever. The `debug` phase is built
to grep there *before* doing any environmental debugging.

The checkpoint is what lets you reset context without losing accuracy: externalize the
load-bearing facts, clear the window, and a fresh session reads the checkpoint first.

---

## Driving the tools directly

| Do | Command |
|---|---|
| Refresh the bundle | `python .clutch/export.py` |
| Pick bundle components | `python .clutch/scripts/configure.py` |
| Browse tags / modes / search | `python .clutch/scripts/library.py tags\|modes\|search <kw>` |
| List available rule files | `python .clutch/scripts/rules.py --list` |
| Grade a commit | `python .clutch/scripts/grade.py [ref]` |
| Session report | `python .clutch/scripts/session_report.py [--history]` |
| Commit in transcript order | `python .clutch/scripts/transcript_commit.py [--commit]` |
| Render a diagram | `python .clutch/scripts/mermaid_export.py <file> --scale 4` |
| Checkpoint | `python .clutch/scripts/checkpoint.py new\|show\|archive` |
| Enforce ASCII output | `python .clutch/scripts/ascii_normalize.py <paths>` |
| Sync memory + libraries | `python .clutch/sync.py` |
| Install into a new project | `clutch init` |
| Propagate a change everywhere | `clutch update` |

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| No marker on real answers | `CLAUDE.md` not loaded, `operating_mode` off, or stale bundle | check `CLAUDE.md` exists, set `operating_mode: true`, run `export.py`, start a new session |
| Receipt is identical every reply | it is being written as boilerplate, not earned | say so - the rules forbid it. Ask which files it actually read |
| It skipped the solutions check while debugging | it did not enter `debug` mode | say "debug mode" explicitly next time |
| Uses em dashes / adds "generated by" | human-output off, or stale bundle | enable in `configure.py`, `export.py`, then `ascii_normalize.py <paths>` |
| Wrong or missing stack rules | `stack` in `config.json` empty or wrong | set it, then `export.py` |
| Solution written but invisible elsewhere | `sync.py` never ran, so `INDEX.md` was not regenerated | `python .clutch/sync.py` |
| No history entry for a session | the hook only fires on `git push` | `python .clutch/scripts/session_report.py --history` |
| Changed the toolkit, other projects stale | nothing propagates on its own | `clutch update` (see `guides/MAINTAINING.md`) |
| A script is missing or outdated | project has an old copy | re-run `clutch init`, or `clutch update` for all |

---

## Where things live

- `.clutch/AI.md` - the bundle the assistant reads (generated, do not hand-edit).
- `.clutch/config.json` - `stack`, `operating_mode`, `bundle_include`.
- `.clutch/{checkpoint,history,solutions}/` - working, episodic, long-term memory.
- `.clutch/scripts/` - the tools.
- `info.md` (project root) - the two-tier project map, kept current as the shape changes.
- `%USERPROFILE%\.clutch\` - the global store: shared guides, prompts, rules, and the
  merged solutions index. Libraries live here **once**; projects read from it.
