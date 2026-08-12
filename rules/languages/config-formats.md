# Config Formats - YAML, JSON, TOML

## Universal

1. **Config is code: version it, review it, validate it.** Schema-validate where tooling exists (JSON Schema, CI checks). A malformed config that fails at deploy is a bug you wrote.
2. **No secrets in config files that touch version control.** Reference environment variables or a secret manager; commit `.example` templates with fake values.
3. **Comments explaining non-obvious values** (why this timeout, where this magic ID comes from) - in formats that support them (YAML, TOML). JSON's lack of comments is a reason to prefer the others for human-edited config (or JSONC where tooling accepts it).
4. **Don't hand-edit generated files** (lockfiles, build outputs) - change the source and regenerate.

## YAML - the footgun format

5. **Quote strings that could be something else.** The Norway problem: `country: NO` parses as `false` (YAML 1.1 parsers); `version: 1.20` becomes a float; `time: 08:30` can become sexagesimal seconds. When in doubt, quote.
6. **Indentation is syntax:** spaces only, consistent width, no tabs. A one-space slip silently changes structure - validate after editing (`yamllint`, or just load it).
7. **Anchors/aliases (`&`, `*`, `<<:`) for repeated blocks sparingly** - great for CI matrices, unreadable past two levels. Know your consumer supports merge keys before using them.
8. **Multiline strings deliberately:** `|` keeps newlines, `>` folds them; `|-`/`|+` control the trailing newline. Wrong choice = subtle bugs in scripts embedded in CI YAML.
9. **Load YAML safely in code:** `yaml.safe_load` (Python) and equivalents - full loaders execute arbitrary constructors.

## JSON

10. **Strict syntax, no exceptions:** double quotes, no trailing commas, no comments (unless the consumer explicitly accepts JSONC - check). One more trailing comma in a JSON file is one broken deploy.
11. **Know your numbers:** JSON numbers are IEEE doubles in most consumers - 64-bit IDs corrupt silently. Transmit big integers and money as strings or minor units.
12. **Stable key ordering and consistent formatting** (match the project's prettier/formatter) so diffs stay reviewable.

## TOML

13. **Understand table semantics before editing:** `[table]` vs `[[array-of-tables]]`, dotted keys, and the rule that once a table is defined you can't reopen it later in the file. Order sections the way the ecosystem convention does (`pyproject.toml`, `Cargo.toml` have established layouts).
14. **Dates, times, and durations are first-class in TOML** - use native datetimes rather than magic strings where the consumer supports it.

## Choosing

15. **Machine-to-machine: JSON. Human-edited app config: TOML (unambiguous) or YAML (if the ecosystem demands it - CI, k8s). Deep nesting is a design smell in any of them** - flatten or split files.
