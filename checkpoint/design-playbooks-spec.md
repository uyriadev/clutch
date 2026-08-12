# Spec: prompts/design/ decision playbooks

_Handoff for the implementing session. The design thinking is DONE - execute exactly
as written, then verify. Do not redesign, do not water down the content. Written
2026-08-09; every wiring claim below was verified against the repo on that date._

## What this adds

A new library category: run-on-demand reasoning playbooks for structural design
decisions. Two playbooks (data structures, function design), a trigger-table README,
and an output-record template. Unlike the sibling prompt fragments (always-on style)
and rules/ (per-stack), a playbook is read only when its trigger fires - the AI.md
bundle carries ONLY the trigger table.

Files to create:

1. `prompts/design/README.md` - trigger table (this is what rides in bundles)
2. `prompts/design/data-structures.md` - playbook
3. `prompts/design/function-design.md` - playbook
4. `templates/design-decision.md` - output record (mini decision-record)

Files to edit:

5. `scripts/configure.py` - register one new COMPONENTS entry
6. `prompts/README.md` - index the new folder
7. `README.md` (root) - one-line tree update

Then: ascii_normalize, `python update_all.py`, verify (steps at the bottom).

## Non-negotiables - acceptance criteria

These are the points weaker reasoning reliably drops. Each MUST survive into the
final files, in substance if not verbatim. If an edit would remove one, the edit is
wrong.

data-structures.md must keep:

- Step 1 (operations) is written down BEFORE any structure is named; if a structure
  name already appeared, restart the step. Operations determine structure, never the
  reverse.
- Small-n trap: under roughly a hundred elements, a linear scan over a contiguous
  array usually beats a hash map (no hashing, no pointer chase, prefetcher wins).
- Linked-list trap: its O(1) middle insert needs an O(n) cache-missing walk to find
  the spot; it is almost never the answer.
- Built-ins are not the textbook, with the named examples (Python list = dynamic
  array; C++ std::map = red-black tree; node-based containers are cache-hostile; Go
  map iteration deliberately randomized; Java HashMap treeifies hot buckets) and the
  instruction to verify against the installed version's docs, not memory.
- Amortized is not worst-case: growth/rehash spikes matter for latency budgets even
  when throughput is fine.
- Composites are allowed (map + ordered array), priced honestly: every extra
  structure is an invariant someone must keep in sync on every mutation.
- Wire/persisted shape does NOT have to equal in-memory shape.
- Developer time is a legitimate deciding constraint - but only when named
  explicitly, never as a silent default.
- "Too close to call" resolves to "measure", never to a fabricated perf claim.
- Step 0: check how the codebase already holds similar data; matching beats foreign
  optimality.

function-design.md must keep:

- Design from the call site inward: write the ideal call site as a line of code
  before the signature.
- Split on responsibility seams (different reasons to change, independently testable
  decision, a real second caller) - never on line count. A cohesive 40-line function
  usually beats four 10-line fragments passing state around ("deep over shallow").
- A boolean parameter is a fork in disguise; prefer two functions or a named enum.
- Error behavior is part of the signature, decided now, matching the codebase's
  existing convention (exceptions vs results) - not personal taste, not bolted on.
- Async is viral (recolors every caller); put it where IO actually happens, never
  "for future-proofing".
- Mutating an argument is API and the classic hidden bug; do not mutate AND return
  derived data (command-query separation).
- Concrete until a second caller with real divergent needs exists; speculative
  hooks/callbacks/generics are the most common AI-generated waste.
- Testability/purity is a constraint on par with CPU or RAM, sometimes the deciding
  one.
- Concrete revisit triggers: second caller diverges, a bool param is about to
  appear, positional params pass ~4, the name needs an "and", profiling shows it
  hot, it needs to become async.

README.md (design/) must keep:

- A "when NOT to run these" section (existing pattern, small/local/short-lived data,
  obvious one-caller private helper) - depth matches stakes.
- The on-demand model stated plainly: only the trigger table rides in the bundle.
- Explicit file paths including the global-store fallback - bundle readers see
  inlined text and cannot follow relative links.

templates/design-decision.md: the filled record stays under ~20 lines - it is the
conclusion, not the transcript.

All files: standard-keyboard characters only (no em dashes), no generated-by
trailers, self-check list at the end of each playbook (house prompt convention).

## Step 1: create prompts/design/README.md

```markdown
# design/ - decision playbooks

Step-by-step reasoning to run BEFORE writing code that commits to a shape: how data
is stored, how a function presents itself to callers. Unlike the sibling prompt
fragments (always-on style) and `rules/` (per-stack), these load on demand - only
this trigger table travels in the AI.md bundle. When a trigger fires, read the full
playbook from `.clutch/prompts/design/` if present, else from the global store at
`%USERPROFILE%\.clutch\prompts\design\`.

## Triggers

| Before you... | Read |
|---|---|
| Commit to how data is stored, accessed, or moved - a new collection, cache, index, queue, or a persisted / wire shape | `prompts/design/data-structures.md` |
| Write or reshape a function, method, or endpoint other code will call - params, return shape, errors, sync vs async, split vs keep | `prompts/design/function-design.md` |

Record the outcome with `templates/design-decision.md` - the distilled conclusion,
not the scratch work - wherever the project keeps design notes (docs, module
docstring, or the PR description).

## When NOT to run these

Depth must match stakes (see `rules/ai/reasoning.md`, depth calibration). Skip the
playbook when:

- The codebase already has a pattern for this exact job - match it and move on.
- The data is small, local, and short-lived (a handful of items inside one function).
- The function is private, has one caller, and its shape is obvious.

Run it when the choice is expensive to reverse, sits on a hot path, crosses a module
or API boundary, or will be persisted or sent over the wire.
```

## Step 2: create prompts/design/data-structures.md

```markdown
# Data structures - choosing the shape of data

Run this BEFORE writing code that commits to how data is stored, accessed, or moved.
Work the steps in order; the doc at the end is the distilled conclusion, not the
scratch work. Pair with the language's `rules/` file for its specifics.

Think like a senior dev doing a design review, not like someone reciting
definitions. A senior dev picks a structure because they traced the actual access
pattern, the actual scale, and the one constraint that matters most here - and
everything else was a worse fit.

## Step 0: check the codebase first

How does this project already hold similar data? Matching the existing pattern beats
a locally-optimal foreign one. If a good pattern exists, use it and go straight to
the output doc. The most common failure is not a bad structure - it is a structure
the rest of the codebase does not use.

## Step 1: name the operations, not the data

List what will actually happen to this data, ordered by frequency:

- Reads: by index, by key, by range, sequential, random?
- Writes: insert or remove at front, back, middle, arbitrary position?
- Does order matter? Does uniqueness? (A set or dict used for dedup silently drops
  duplicates - confirm that IS the wanted semantic, not a side effect.)
- Read-heavy, write-heavy, or roughly even?
- Scale: order of magnitude now, and does it grow over the project's life?

Do not name any structure yet. If a structure name has already appeared in your
notes, you skipped this step - start over. Operations determine the structure,
never the reverse.

## Step 2: name the constraint that actually matters

Pick the one or two resources this code is most sensitive to, and say why:

- **CPU / cache** - hot loops, per-frame, per-request. Memory layout and locality
  dominate here, not Big-O.
- **RAM** - large in-memory datasets, mobile or embedded targets. Per-element
  overhead matters more than asymptotics.
- **Disk / IO** - persisted or bigger-than-memory data; access patterns to storage
  (B-tree vs LSM vs flat-file territory).
- **GPU** - parallel or offloaded work; struct-of-arrays vs array-of-structs and
  transfer overhead.
- **Network** - wire size and shape matter as much as in-memory shape. The wire
  shape does NOT have to equal the in-memory shape - serializing a different one is
  normal.
- **Developer time / extensibility** - the simpler, slightly slower structure is a
  legitimate winner for code touched constantly. Legitimate only when named
  explicitly as the deciding constraint - never as a silent default.

If the user named a constraint (CPU, GPU, disk, RAM), that is the lens every
candidate is judged through.

## Step 3: real candidates, including the boring one

List two or three structures that could work. The plain array/list/dict default is
always one of them - as a real candidate, not a strawman. For each:

- Complexity for the Step 1 operations, including the worst case where it bites
  (hash lookups degrade to O(n); amortized O(1) append still has O(n) growth
  spikes, which matters for latency budgets even when throughput is fine).
- Space overhead per element, not just asymptotics.
- Behavior under the Step 2 constraint ("sorted array: great locality, O(log n)
  search, O(n) middle insert").
- Whether the language built-in matches the textbook. It often does not - verify
  against the installed version's docs, not memory. Known gaps: Python's list is a
  dynamic array, not a linked list, and dicts carry real per-entry overhead; C++
  std::map is a red-black tree, and node-based containers are cache-hostile; Go
  randomizes map iteration order on purpose; Java's HashMap treeifies hot buckets.
  Assert only what you verified this session (see `guides/AI-PITFALLS.md`).

Discard nothing silently - one line on why each rejected option loses.

Traps that separate real reasoning from recitation:

- **Small n beats Big-O.** Under roughly a hundred elements, a linear scan over a
  contiguous array usually beats a hash map: no hashing, no pointer chase, the
  prefetcher does the work. Do not pick the O(1) structure for 12 items.
- **The linked list is almost never the answer.** Its O(1) middle insert requires
  an O(n) cache-missing walk to find the spot. If middle insertion is truly hot,
  reconsider the layout (gap buffer, chunked array, tree) instead.
- **Composites are allowed.** A dict index over an ordered array is often the real
  answer. Price it honestly: every extra structure is an invariant someone must
  keep in sync on every mutation - name who maintains it.

## Step 4: state the trade-off

One or two sentences, plain terms, rejected alternative visible:

- "Struct-of-arrays over array-of-structs: this loop runs every tick and touches
  two fields; the readability cost is real but confined to one module."
- "Plain list with linear search over a dict: under ~50 items the scan wins on
  locality with no hashing; the dict returns if the roster grows."

If the honest answer is "too close to call without numbers", the conclusion is
measure - never a fabricated performance claim.

## Step 5: name the revisit condition

The observable condition under which to reconsider: a scale threshold, a read/write
ratio flip, going multi-threaded, moving to GPU. "Revisit if it gets slow" is not a
condition; "revisit when n passes ~10k or deletes become common" is.

## Output

Record the conclusion with `templates/design-decision.md`: the chosen structure(s)
and their operations, the Step 4 trade-off, complexity notes relevant to the actual
usage (not a textbook table), and the Step 5 revisit condition. Keep it short - the
steps above are scratch work.

## References (verified, non-blog)

- MIT OCW 6.006, Introduction to Algorithms - https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/
- Python TimeComplexity wiki - https://wiki.python.org/moin/TimeComplexity
- cppreference, Containers library - https://en.cppreference.com/w/cpp/container
- Oracle, Java Collections Framework Overview - https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/doc-files/coll-overview.html
- Drepper, What Every Programmer Should Know About Memory - https://akkadia.org/drepper/cpumemory.pdf
- Nystrom, Game Programming Patterns, Data Locality - https://gameprogrammingpatterns.com/data-locality.html

## Self-check

- [ ] Step 1 was written before any structure was named.
- [ ] The boring default was evaluated as a real candidate.
- [ ] Every complexity or perf claim is verified for the installed version,
      measured, or flagged "measure".
- [ ] The trade-off names the rejected alternative and the reason.
- [ ] The revisit condition is observable, not "if it gets slow".
```

## Step 3: create prompts/design/function-design.md

```markdown
# Function design - shaping the signature

Run this BEFORE writing or reshaping a function, method, or endpoint that other code
will call - or before splitting one apart. Work the steps in order; the doc at the
end is the conclusion, not the transcript. Pair with `prompts/code-craft.md`
(naming, right-sized abstraction) and the language's `rules/` file (idioms).

A signature is an API contract, even module-private: every parameter, return shape,
error path, and side effect is something callers depend on. Design it from the call
site inward, not from the body outward.

## Step 0: check the codebase first

How do neighboring functions take arguments, report errors, and handle async? Match
the local convention - a result-tuple function in an exceptions codebase is a
defect even if you prefer result tuples.

## Step 1: name the call sites, not the body

- Who calls this, how often, and what varies between calls? Write the ideal call
  site as a line of code FIRST - the signature falls out of what reads well there,
  not out of the body's convenience.
- What does it truly need as input, vs what merely happens to be lying around in
  the caller?
- What comes out - a value, a mutation, IO? On failure, what exactly does each
  caller need in order to react?
- Is there a real second caller today, or only a hypothetical one?

## Step 2: name the dominant force

Pick the one or two that rule this function, and say why:

- **Readability at the call site** - the default winner for most code.
- **Testability** - can the decision be tested without the IO? Purity is a
  constraint on par with CPU or RAM, and sometimes the deciding one.
- **Hot-path performance** - allocation per call, copies at the boundary.
- **API stability** - public or cross-module surface that is expensive to change.
- **Reuse** - only with evidence: a second caller that exists.

## Step 3: real candidates

Consider at least two shapes, including the boring one (a single plain function).
Each of the following is part of the signature - decide it explicitly:

- **One function vs a split.** Split on responsibility seams: different reasons to
  change, an independently testable decision, a real second caller. Never on line
  count. A cohesive 40-line function with one caller usually beats four 10-line
  fragments passing state to each other - hide meaningful work behind a small
  interface, not a thin wrapper over another call.
- **Parameters.** Positional up to ~3-4; past that, keyword or options object -
  but no config-object indirection for two params. A boolean parameter is a fork
  in disguise: `render(data, true)` is unreadable at the call site and means the
  function does two things - prefer two functions or a named enum.
- **Errors.** Exception vs result/optional vs sentinel - per the Step 0 codebase
  convention, decided now, visible in the signature or docs, not bolted on later.
  Every error a caller must handle is API surface.
- **Sync vs async.** Async is viral - it recolors every caller up the stack. Put
  it where IO actually happens; never "async for future-proofing".
- **Mutate vs return.** Mutating an argument is API and the classic hidden bug.
  Default to returning a new value; mutate only deliberately, with the verb saying
  so (`sort` vs `sorted`). Do not mutate AND return derived data - command-query
  separation keeps callers sane.
- **Concrete vs generic.** One caller = concrete. Generalize on the second caller
  with real divergent needs, not before. Hooks, callbacks, and strategy parameters
  for callers that do not exist are the most common generated-code waste.

## Step 4: state the trade-off

One or two sentences with the rejected shape visible:

- "Kept it one 40-line function: the three phases share all their locals and have
  no independent callers; splitting adds a parameter-passing tax and buys nothing."
- "Two functions instead of a flag: `export_csv` / `export_json` cost a little
  duplication, but every call site now says what it does."

## Step 5: name the revisit condition

Typical triggers - name the ones that apply: a second caller shows up wanting
different behavior; a boolean parameter is about to appear; positional params pass
~4; the name needs an "and"; profiling shows it hot; it needs to become async.

## Output

For boundary or API decisions, record with `templates/design-decision.md`. For a
private helper, a one-line comment naming the rejected shape is enough.

## References (verified, non-blog)

- Ousterhout, A Philosophy of Software Design (deep vs shallow modules) - talk: https://www.youtube.com/watch?v=bmSAYlu0NcY
- Google Engineering Practices - https://google.github.io/eng-practices/
- Bloch, How to Design a Good API and Why it Matters - https://research.google/pubs/pub32713/

## Self-check

- [ ] I wrote the ideal call site before the signature.
- [ ] No boolean flag param; params stay <= ~4 or go keyword.
- [ ] Error behavior is decided and matches the codebase convention.
- [ ] Nothing is generic or hooked for a caller that does not exist.
- [ ] Any argument mutation is deliberate and visible in the name.
- [ ] The trade-off names the rejected shape.
```

## Step 4: create templates/design-decision.md

```markdown
# Design decision - {what was chosen, for what}

_{date}. Output of a `prompts/design/` playbook. Keep the filled record under ~20
lines - it is the conclusion, not the scratch work. File it where the project keeps
design notes (docs, module docstring, or the PR description)._

## Decision
<!-- One line. "Ring buffer (collections.deque, maxlen=1000) for frame-time history." -->

## Driving facts
<!-- The 2-4 Step 1/2 facts that decided it: operations by frequency, scale, the
     one constraint that ruled. -->
-

## Rejected
<!-- Each real alternative, one line: name + why it lost. -->
-

## Trade-off
<!-- The Step 4 sentence(s), verbatim. -->

## Complexity / footprint notes
<!-- Only what matters for the actual usage. Mark each: measured / verified from
     docs / assumed. -->
-

## Revisit when
<!-- Observable condition(s): scale threshold, read-write flip, second caller,
     going async or parallel. -->
-
```

## Step 5: register the bundle component

In `scripts/configure.py`, append this tuple to `COMPONENTS` (after the
`flowcharts` entry, before the closing `]`). Do NOT reorder existing entries - the
bundle emits prompts in registry order.

```python
    ("design-playbooks", "Prompt", "prompts/design/README.md",
     "Design playbooks (trigger table)",
     "Decision playbooks for structural choices (data structures, function design). "
     "Only the trigger table rides in the bundle; the full playbook is read from "
     "prompts/design/ when a trigger fires. Recommended on."),
```

Why README.md and not the playbooks: the playbooks are ~120 lines each and are
load-on-demand by design. Registering the full files would bloat every project's
AI.md with content that is only needed at design time. This is deliberate - do not
"helpfully" register data-structures.md or function-design.md as components.

## Step 6: update the indexes

`prompts/README.md` - append this section after the existing table / "How to use"
material (keep the existing table untouched):

```markdown
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
```

Root `README.md`, line ~75, currently:
`├── prompts/               reusable prompt fragments; source-only, global is canonical`
Append ` (+ design/ decision playbooks)` inside that line's description.

`info.md`: NO change - its libraries row is generic and still accurate. Do not
invent an edit.

`guide.md`: NO change.

## Step 7: normalize and propagate

Run from the repo root:

```
python scripts/ascii_normalize.py prompts/design/README.md prompts/design/data-structures.md prompts/design/function-design.md templates/design-decision.md prompts/README.md README.md
python update_all.py
```

update_all is mandatory here for TWO reasons: the library changed (sync) AND a
toolkit script changed (configure.py must be republished via install_global.py to
the global toolkit, or consumer installs keep the old COMPONENTS registry).

## Step 8: verify (all four, report results honestly)

1. Global store has the folder:
   `Get-ChildItem "$env:USERPROFILE\.clutch\prompts\design"` -> 3 files;
   `Test-Path "$env:USERPROFILE\.clutch\templates\design-decision.md"` -> True.
2. The source repo's own bundle carries the trigger table:
   `python export.py --stdout | Select-String "decision playbooks"` -> matches.
3. The republished toolkit registry has the entry:
   `Select-String "design-playbooks" "$env:USERPROFILE\.clutch\toolkit\scripts\configure.py"` -> matches.
4. Reference URLs: fetch each URL in both playbooks' References sections. Delete
   any line that 404s. Do NOT add replacement URLs you have not fetched.

## Known gotcha: existing consumers with an explicit bundle_include

`included()` in configure.py returns True only if `bundle_include` is None (never
configured -> everything on) or the key is in the list. Consumer projects that ran
the component picker have a persisted list WITHOUT "design-playbooks", so the
trigger table will not enter their bundles until the key is added. New installs get
it by default. This is expected behavior, not a bug - leave those configs alone and
mention it in the final report to the user, who can opt projects in by adding
"design-playbooks" to that project's `.clutch/config.json` `bundle_include` and
rerunning update_all.

## Wiring facts already verified (do not re-derive, do not doubt)

- sync.py mirrors `prompts/` recursively via `newer_wins_tree` (rglob), so the
  design/ subfolder propagates; `templates/` mirrors flat via `newer_wins`
  (sync.py lines ~56-131).
- `find_resource`/`read_resource` (scripts/_common.py) join arbitrary relpaths, so
  `prompts/design/README.md` resolves local-first then global for consumers.
- export.py includes a Prompt component's full text in the "Prompt fragments"
  section only if `cfg_mod.included()` says so (export.py lines ~100-109); the
  COMPONENTS registry in scripts/configure.py is the single source of truth.
- The repo is not a git repo (no commit steps needed).
- ascii_normalize.py replaces non-keyboard characters per prompts/human-output.md;
  the bundle build also normalizes, but library sources must be clean themselves.
