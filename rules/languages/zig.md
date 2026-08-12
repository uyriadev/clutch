# Zig

1. **Pin the exact Zig version** (`build.zig.zon` / project docs). Zig is pre-1.0 - std APIs and syntax change between 0.x releases; code from memory is likely stale. Verify against the project's actual version.
2. **Allocators are explicit and passed in.** Any function that allocates takes an `Allocator` parameter. Never stash a global allocator; the caller chooses the strategy. In tests use `std.testing.allocator` (it detects leaks).
3. **Every allocation has a paired `defer` free** at the acquisition site (`defer allocator.free(buf)`, `defer list.deinit()`), or transfers ownership explicitly (name it `toOwnedSlice`-style intent). `errdefer` for cleanup on the error path when ownership transfers on success.
4. **Errors are values in error unions:** return `!T`, handle with `try` (propagate), `catch` (handle with a value/block), or exhaustive `switch` on the error set. Never `catch unreachable` on errors that can actually occur - that's UB in release-fast.
5. **`unreachable`, `undefined`, and `@ptrCast`-family are contracts with the optimizer:** `undefined` reads are UB; use them only where the invariant is locally provable, comment why. Prefer `std.debug.assert` for checked invariants.
6. **Optionals over sentinels:** `?T` with `orelse` / `if (x) |v|` unwrapping. Null-terminated types (`[:0]u8`) only at C boundaries.
7. **comptime is a power tool, not a default:** use it for generics (`fn Foo(comptime T: type)`), config, and table generation; keep comptime logic small and readable - heavily meta code reviews terribly.
8. **Slices over pointers-plus-length everywhere possible;** know the pointer taxonomy (`*T`, `[*]T`, `[]T`, `[*:0]T`) and don't cast between them casually.
9. **Integer overflow traps in safe modes:** use explicit wrapping (`+%`)/saturating (`+|`) operators when wraparound is intended; otherwise fix the bounds. Cast with `@intCast`/`@truncate` deliberately - they assert in safe builds.
10. **Follow std lib style:** `camelCase` functions, `TitleCase` types, `snake_case` fields/variables; `zig fmt` output unedited; small explicit structs over clever abstraction.
11. **Build and test through `build.zig`:** `zig build test` runs the test blocks (`test "name" {}`) colocated with code - write them there, and keep C interop (`@cImport`/linking) declared in the build script, not ad-hoc.
