# Performance Awareness

Rules for writing code that's fast enough without premature optimization.

## The prime directive

1. **Measure before optimizing; don't pessimize by default.** Never restructure code for speed without a profile showing it matters. But equally: don't write gratuitously slow code (accidentally quadratic loops, queries in loops) just because "premature optimization is bad." The rule is *no unmeasured cleverness*, not *no thought*.

## The classics - avoid these without needing a profiler

2. **N+1 queries.** Fetching a list then querying per item is the most common real-world performance bug. Use joins, `IN` clauses, ORM eager loading (`select_related`/`prefetch_related`, `include`, `joinedload`), or batch endpoints.
3. **Unbounded queries.** Every list query gets a `LIMIT`/pagination. Every table scan on a filtered column gets an index question. "It was fine with test data" is how production dies.
4. **Accidentally quadratic.** `list.contains` inside a loop over another list, string concatenation in a loop, repeated `array.indexOf` - use sets/maps for membership, builders/join for strings.
5. **Sequential awaits on independent work.** Independent I/O runs concurrently (`Promise.all`, `asyncio.gather`, goroutines). Awaiting three unrelated fetches in series triples your latency for nothing.
6. **Reading entire files/results into memory when streaming works.** Anything user-sized (uploads, exports, log processing) streams; only known-small data loads whole.
7. **Work inside hot loops that could happen once.** Regex compilation, date formatter construction, config parsing - hoist out of the loop.

## Caching

8. **Cache only measured hot spots, and always answer two questions first:** how is it invalidated, and what happens when it's stale? A cache without an invalidation story is a bug with good latency.
9. **Never cache per-user data in a shared scope** (module-level dict in a web worker, static field in a servlet). That's a data leak, not a speedup.

## Frontend specifics

10. **Bundle size is a feature.** Check the cost of a dependency before importing it; prefer tree-shakeable imports (`import { x }` from the specific module, not the barrel).
11. **Don't fight the framework's rendering model.** In React, that means stable keys, state colocated where it's used, memoization only for measured re-render problems - not `useMemo` sprinkled everywhere as superstition.
12. **Images and fonts dominate most page weights.** Right-sized, modern-format images (framework `<Image>` components where available), font subsetting/`display: swap` - before micro-optimizing JS.

## Honest trade-offs

13. **State the complexity when it's non-obvious.** If your solution is O(n^2) but n is bounded at ~20, say so - that's a fine choice made visible, not a hidden trap.
14. **Readability wins ties.** Optimizations that obscure logic need a measured justification recorded in a comment ("~40ms -> 2ms on the search hot path"), or they revert to the readable version.
