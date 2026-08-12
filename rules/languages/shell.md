# Shell - Bash & PowerShell

## Bash

1. **Open with the safety header:** `#!/usr/bin/env bash` and `set -euo pipefail`. Know its limits (`-e` is disabled in conditionals and command substitutions in some contexts) - check critical exit codes explicitly anyway.
2. **Quote every expansion:** `"$var"`, `"$@"`, `"$(cmd)"`. Unquoted variables word-split and glob - the single most common shell bug. `shellcheck` is mandatory; fix every finding or justify the directive comment.
3. **`[[ ]]` over `[ ]`** for tests (no word-splitting, supports `&&`, `=~`); arithmetic in `(( ))`.
4. **Never parse `ls`;** glob (`for f in *.txt`) or `find -print0 | xargs -0` / `while IFS= read -r -d ''` for filenames with spaces. Handle the no-match case (`nullglob` or an existence check).
5. **User input never touches `eval` or becomes part of a command string.** Build argument lists with arrays: `args=(-v --file "$f"); cmd "${args[@]}"`.
6. **Temp files via `mktemp`, cleanup via `trap 'rm -rf "$tmpdir"' EXIT`.** Check `cd` success (`cd /x || exit 1`) - a failed `cd` followed by `rm -rf *` is a career event.
7. **Functions + `local` variables for anything over ~30 lines;** past ~100 lines or needing data structures, the answer is Python, not more Bash.
8. **Portability is explicit:** if it must run on `sh`/dash/macOS's old Bash 3.2, avoid bashisms (arrays, `[[ ]]`) accordingly - decide the target, note it at the top.

## PowerShell

9. **PowerShell pipes objects, not text** - filter with `Where-Object`, project with `Select-Object`, don't regex-parse formatted output. `Format-*` cmdlets are for display only, never mid-pipeline.
10. **Error handling:** `-ErrorAction Stop` + `try/catch` for cmdlets you need to react to; check `$LASTEXITCODE` after native executables (they don't throw). `$?` reflects only the previous statement.
11. **Verb-Noun naming for functions (approved verbs), PascalCase parameters, `[CmdletBinding()]`** with typed parameters and `[Parameter(Mandatory)]` over manual arg-parsing.
12. **Version awareness:** Windows PowerShell 5.1 lacks `&&`/`||`, ternary, `??` - know which edition the script targets. Encoding differs too (5.1 defaults UTF-16 for redirects; pass `-Encoding utf8` when other tools consume the file).
13. **Destructive cmdlets get `-WhatIf` support:** implement `SupportsShouldProcess` in your own functions; test with `-WhatIf` before running for real.

## Both

14. **Scripts are idempotent where possible** (re-running shouldn't compound damage) and fail loudly with a usage message on bad arguments.
15. **No secrets in command lines** (visible in process lists and history) - use env vars, stdin, or credential stores.
