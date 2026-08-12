# Rust

## Work with the borrow checker, not around it

1. **Restructure before you `clone()`, `clone()` before you `Rc<RefCell<>>`, and reach for `unsafe` essentially never.** Fighting lifetimes usually means the ownership design is wrong - fix who owns what. That said, a `.clone()` of small data to unblock is honest and fine; note it if it's on a hot path.
2. **`unsafe` requires a `// SAFETY:` comment stating the invariant that makes it sound,** and the smallest possible scope. No unsafe to "make the compiler stop complaining."
3. **Borrow (`&T`/`&str`/`&[T]`) in parameters; own (`String`/`Vec<T>`) when you store.** Don't take `String` when `&str` works.

## Errors

4. **`Result` for recoverable errors, `panic!`/`unwrap` for genuine impossibilities.** `.unwrap()`/`.expect()` in library code or on external input is a bug; `expect("why this can't fail")` in binaries/tests is acceptable with a real reason.
5. **`?` to propagate; don't ladder `match` on every fallible call.**
6. **Applications: `anyhow` (or eyre) for error plumbing with `.context()`. Libraries: concrete error types via `thiserror`.** Match the crate's existing choice.
7. **Handle `Option` with combinators where clear** (`map`, `and_then`, `ok_or`, `unwrap_or_else`) and `if let`/`let else` where control flow is clearer than chaining.

## Idioms

8. **`clippy` clean, `rustfmt` formatted.** Clippy lints are code review from the compiler team - fix rather than `#[allow]`, and justify any `allow` in a comment.
9. **Iterators over index loops.** Chained iterator adapters compile to the same code as the loop and eliminate bounds-check noise. `collect()` into the right container with turbofish or inference.
10. **Derive liberally:** `Debug` on everything public, plus `Clone`, `PartialEq`, `Default`, `serde` traits as appropriate. Implement `Display` for user-facing types, `From` for conversions (which gives you `Into` and `?` coercion).
11. **Make illegal states unrepresentable:** enums with data over struct-with-flags, newtypes (`struct UserId(u64)`) over bare primitives that could be swapped.
12. **Match exhaustively; avoid `_` arms on enums you own** - a wildcard arm silently absorbs future variants that should have forced a decision.

## Structure and async

13. **Keep `pub` minimal;** every public item is API surface you maintain forever. `pub(crate)` for internals shared across modules.
14. **Async: don't hold non-async locks or `RefCell` borrows across `.await` points** (deadlock/panic bait). Use `tokio::sync` primitives in async code; spawn blocking work with `spawn_blocking`.
15. **Know the runtime the project uses (almost always tokio) and its version;** async trait support and APIs shifted across editions - check `Cargo.toml` before writing from memory.
16. **Tests live in `#[cfg(test)] mod tests` beside the code; integration tests in `tests/`.** Doc examples (`///` with code fences) compile and run in CI - keep them true.
