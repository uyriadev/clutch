---
title: Function design - shaping the signature
tags: [function, signature, parameters, api, errors, async, refactor]
modes: [plan]
order: 32
---

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
