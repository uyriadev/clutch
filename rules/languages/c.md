# C

## Memory - the whole game

1. **Every allocation has one owner and one documented free path.** State ownership in the function contract ("caller frees", "borrowed, valid until X"). If you can't say who frees it, the design is incomplete.
2. **Check every allocation.** `malloc` returns NULL; so do `fopen`, `calloc`, `realloc`. `realloc` pattern: assign to a temp, check, then replace - `p = realloc(p, n)` leaks on failure.
3. **NULL out pointers after free** where the pointer outlives the free; never double-free, never use-after-free. Prefer a single cleanup exit (`goto cleanup`) for functions with multiple resources - it's the one respectable `goto`.
4. **sizeof the object, not the type:** `p = malloc(count * sizeof *p)` survives type changes; check for multiplication overflow on untrusted counts.

## Buffers and strings

5. **Every buffer write is bounds-checked.** Banned outright: `gets`, `sprintf` into fixed buffers, `strcpy`/`strcat` on untrusted input. Use `snprintf` (and check its return - it reports truncation), or length-explicit APIs.
6. **C strings must be NUL-terminated and you must prove it.** `strncpy` does not guarantee termination - that's its famous trap.
7. **Never mix signed/unsigned in comparisons carelessly** - `if (len - 1 > x)` with unsigned `len == 0` wraps to a huge number. Compile with `-Wall -Wextra -Wconversion` and fix, not silence.

## Undefined behavior is not "works on my machine"

8. **UB is a landmine, not a performance trick:** signed overflow, out-of-bounds access, strict-aliasing violations, uninitialized reads, NULL deref. The compiler may delete your safety checks based on assuming UB never happens.
9. **Initialize variables at declaration.** Uninitialized reads are UB and pass tests by accident.
10. **Test under sanitizers:** `-fsanitize=address,undefined` in debug builds catches what code review can't. Valgrind where sanitizers can't run.

## Structure and hygiene

11. **`const` everything that doesn't mutate:** pointer parameters (`const char *`), lookup tables (`static const`). It's documentation the compiler enforces.
12. **`static` for file-local functions and globals** - minimize the linker-visible surface.
13. **Header discipline:** include guards (or `#pragma once` per project convention), headers include what they use, no function definitions in headers (inline aside).
14. **Macros are a last resort:** prefer `enum`/`static const` for constants, functions for logic. When a macro is necessary: parenthesize parameters and the whole body, uppercase name, beware double evaluation (`MAX(x++, y)`).
15. **Check return values of I/O:** `fread`/`fwrite` short counts, `fclose` (yes, it can fail and lose buffered data), `snprintf` truncation.
16. **Match the project's C standard** (`-std=c99/c11/c17`) and compiler flags; don't introduce C23 features into a C99 embedded codebase.
