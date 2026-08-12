---
title: Data structures - choosing the shape of data
tags: [data-structure, complexity, cache, big-o, array, hashmap, storage]
modes: [plan]
order: 30
---

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
