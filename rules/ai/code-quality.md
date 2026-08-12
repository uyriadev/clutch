# Code Quality Universals

Language-agnostic rules for the code an AI writes.

## Blending in

1. **Match the surrounding code.** Naming style, comment density, error-handling idiom, import ordering, test structure - copy what's already there. Code that stands out as "AI-written" is a maintenance smell even when correct.
2. **Reuse before writing.** Check for an existing helper, util, or library function before implementing one. Duplicating an existing capability is a bug in the review sense even if it runs.
3. **Respect the project's tools.** If there's a formatter, run it. If there's a linter config, obey it - don't disable rules inline to make your code pass.

## Naming and structure

4. **Names state what, precisely.** `getUserById` not `getData`; `retryDelayMs` not `delay`. Include units in names for durations, sizes, and money. A name that requires reading the body to understand has failed.
5. **Functions do one thing at one level of abstraction.** If you need "and" to describe it, split it. If a function mixes business logic with byte-shuffling, extract the byte-shuffling.
6. **Keep nesting shallow.** Early returns over nested conditionals. Guard clauses at the top; the happy path reads straight down.
7. **No dead code, ever.** No commented-out blocks, no unused parameters "for later," no unreachable branches, no exported-but-never-imported helpers. Version control remembers; the source file shouldn't have to.

## Comments

8. **Comments explain why, never what.** The code shows what it does. Comment the non-obvious: the constraint that forced this design, the spec quirk being worked around, the invariant callers must uphold.
9. **Never write comments narrating the change** ("added this to fix the bug", "new function", "updated per request"). Those address the reviewer, not the future reader, and rot instantly.
10. **Delete comments the code has outgrown.** A wrong comment is worse than no comment.

## Errors and edge cases

11. **Handle errors at the level that can act on them.** Don't catch-and-log-and-continue at every layer. Either recover meaningfully, add context and rethrow, or let it propagate.
12. **Never swallow exceptions silently.** An empty catch block is a landmine. At minimum, the failure must be observable.
13. **Validate at boundaries, trust inside.** Parse and validate external input (user input, API responses, file contents) at the edge; internal functions may assume validated data rather than re-checking everywhere.
14. **Make invalid states unrepresentable where the language allows** - enums over string flags, non-nullable types over defensive null checks, closed unions over boolean blindness.

## Dependencies and magic

15. **No new dependencies without cause.** Adding a package for one function you could write in ten lines trades a permanent supply-chain liability for a minute of convenience.
16. **No magic values.** Numbers and strings with meaning get named constants. `86400` is a mystery; `SECONDS_PER_DAY` isn't.
17. **Hardcode nothing environment-specific.** Paths, URLs, ports, credentials - config, not source.
