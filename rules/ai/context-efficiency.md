# Context Efficiency

Rules for how an AI should explore a codebase economically - spending reads where they pay.

## Search strategy

1. **Search, then read - never scan.** Use grep/glob to locate the relevant code, then read those specific files. Reading directories wholesale to "get familiar" burns context on code that doesn't matter to the task.
2. **Search for the distinctive string.** Error messages, user-visible labels, unusual identifiers - grep for the most unique token available. Searching `error` finds everything; searching `"payment declined by issuer"` finds the file.
3. **Read the right portion.** For large files, read the region around your search hit, plus the imports. Whole-file reads are for small files or when structure genuinely matters.
4. **Parallelize independent lookups.** Multiple searches or file reads with no dependency between them go out in one batch, not a sequence of round trips.
5. **Trace, don't guess, call graphs.** To understand a function: read it, grep its callers, read its non-obvious callees. Follow actual references rather than assuming from names.

## Not re-doing work

6. **Trust what you've established.** Facts confirmed earlier in the session (file contents you read, tests you ran, versions you checked) don't need re-verification unless something changed them. Re-reading unchanged files is pure waste.
7. **Note load-bearing facts as you find them.** When a discovery changes your plan ("auth is handled by middleware, not per-route"), record it in your working notes/response so it survives context compression.
8. **Don't re-derive project conventions per file.** Establish them once (from a few representative files or the lint config) and apply them everywhere.

## Right-sizing exploration

9. **Match exploration depth to task size.** A one-line fix needs the function and its tests, not the architecture. A cross-cutting refactor needs the map first. Escalate only when a cheap look proves insufficient.
10. **Entry points reveal structure fastest:** the routes file, the main/index, the DI container, the schema. One of these usually maps the territory better than ten random files.
11. **Config files are dense context:** `package.json`/`pyproject.toml`/`go.mod` (deps + scripts), CI config (how it's really built and tested), lint config (the actual style rules). Read these before forming opinions about a repo.
12. **Stop when the answer stops changing.** If the last three files you read confirmed what you already believed, exploration is done - act.

## Output economy

13. **Don't echo code back unchanged.** Reference locations (`file.ts:42`) instead of pasting blocks the user already has.
14. **Summarize evidence, cite the source.** "The retry cap is 3 (config/queue.ts:17)" beats pasting forty lines of config.
