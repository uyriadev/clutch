# How clutch works

Four views of the same system: what the AI does in a session, how a file decides
whether it ships in the bundle or waits on disk, the three ways a prompt gets
retrieved, and how a change reaches every project.

Diagrams are `stateDiagram-v2` per `prompts/flowcharts.md`. Render them with
`python scripts/mermaid_export.py ARCHITECTURE.md --scale 4`.

---

## 1. A session: load once, then switch phases

The core loads one time and stays resident. Everything after that is a phase
change, and each phase has an exit checklist that gates the next one.

```mermaid
stateDiagram-v2
    direction TB

    [*] --> Load
    Load : Read .clutch/AI.md once and cache it
    Load --> Core
    Core : Core resident - persona, pitfalls, memory API, comms, commit, propagation
    Core --> Route : request arrives

    state Route <<choice>>
    Route --> Plan : 3+ files or competing approaches
    Route --> Code : approach already settled
    Route --> Debug : broken, cause unknown
    Route --> Review : auditing a diff
    Route --> Wrap : done, or context about to reset

    Plan : plan mode - modes/plan.md plus a design playbook if a shape is at stake
    Code : code mode - modes/code.md
    Debug : debug mode - modes/debug.md, grep solutions before anything else
    Review : review mode - modes/review.md plus GRADING.md
    Wrap : wrap mode - modes/wrap.md

    Plan --> Code : checkpoint written, risky assumption verified
    Debug --> Code : root cause named as a mechanism
    Review --> Code : defects to fix
    Code --> Review : substantial change
    Code --> Wrap : verified, small change
    Review --> Wrap : report only
    Wrap --> [*] : memory persisted, propagation run
```

The AI picks the phase itself from the request. The user can override by naming one
("plan mode", "/debug"), and that always wins.

---

## 2. Where a file goes: inlined, or waiting on disk

Frontmatter is the switch. `modes: [core]` means the file is already in the window,
so a phase never re-reads it - a phase only ever names what is new.

```mermaid
stateDiagram-v2
    direction LR

    [*] --> Meta
    Meta : prompts/ and guides/ declare title, tags, modes, order

    Meta --> Sort
    state Sort <<choice>>
    Sort --> Enabled : modes includes core
    Sort --> Deferred : phase-only file

    Enabled : configure.py COMPONENTS gates it on or off per project
    Enabled --> Strip
    Strip : export.py strips frontmatter and inlines the full text
    Strip --> Bundle

    Deferred : stays on disk
    Deferred --> Router
    Router : only its name, trigger, and read line enter the mode table
    Router --> Bundle

    Bundle : .clutch/AI.md - one file the assistant reads
    Bundle --> [*]
```

The cost of `core` is permanent context; the cost of `deferred` is one extra read
when the phase starts. That is the whole trade-off.

---

## 3. Three ways a prompt gets found

Most loading is automatic. The manual paths exist for when you know what you want
and the router does not.

```mermaid
stateDiagram-v2
    direction TB

    [*] --> Need
    Need : some guidance is needed

    Need --> Auto : it is core
    Need --> Phase : a work phase started
    Need --> Hunt : neither - you are looking for something specific

    Auto : already in AI.md, zero calls
    Phase : router names the read line, AI runs it unprompted
    Hunt : library.py search KEYWORD, or the skills browser

    Hunt --> Line
    Line : matched files come back as one read line
    Phase --> Line

    Auto --> Applied
    Line --> Applied
    Applied : guidance in context, work proceeds
    Applied --> [*]
```

Keyword search matches `tags` first, then title, then path - so
`library.py search encoding` finds the file whose tags carry it, not just one whose
name happens to.

---

## 4. Propagation: nothing moves on its own

The standing rule from `guides/MAINTAINING.md`. A change that is not propagated is
not finished.

```mermaid
stateDiagram-v2
    direction LR

    [*] --> Edit
    Edit : change a prompt, guide, rule, or script in the source repo
    Edit --> Run : clutch update

    Run --> Sync
    Sync : sync.py pushes libraries to the global store
    Sync --> Publish
    Publish : install_global.py republishes scripts into toolkit/
    Publish --> Each

    Each : for every registered project - clutch init --defaults
    Each --> Rebuild
    Rebuild : export.py rebuilds that project's AI.md
    Rebuild --> Done

    Done : every project current, no stale bundles
    Done --> [*]

    note right of Run : skip this and every other project keeps the old copy
```

`library.py` is published with the rest of `scripts/`, so consumer projects resolve
mode files out of the global store without carrying the markdown themselves.
