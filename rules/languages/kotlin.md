# Kotlin

## Null safety - use it, don't defeat it

1. **`!!` is a code smell with two legitimate uses:** tests, and invariants you can justify in a comment. Prefer `?.`, `?:`, `let`, `requireNotNull(x) { "why" }` - which at least states the assumption.
2. **Don't over-nullable your own APIs.** A `String?` that's never actually null pushes `?.` noise onto every caller. Make types non-null at the boundary (validate once) and keep them non-null inside.
3. **`lateinit` for framework-injected lifecycles only;** everywhere else, constructor injection or nullable-with-reason.

## Data modeling

4. **`data class` for value carriers; `copy()` for modification; `val` over `var` throughout.** Immutable collections (`List`, `Map`) in signatures; `Mutable*` types are implementation details.
5. **Sealed classes/interfaces for closed hierarchies** (UI state, results, events) with exhaustive `when` - no `else` branch on sealed types, so new variants break the build loudly.
6. **Extension functions for utility ergonomics on types you don't own;** don't use them to hide what should be a class's own responsibility.

## Idioms

7. **Scope functions with restraint:** `let` for null-safe transforms, `apply` for object configuration, `also` for side effects. Nested scope functions with ambiguous `it`/`this` are worse than plain code.
8. **Expression syntax where it clarifies:** single-expression functions, `when` as an expression, `if` as an expression. Don't force it for multi-branch logic.
9. **Named and default arguments over telescoping overloads and builder ceremony.**
10. **Collections pipeline (`map`/`filter`/`groupBy`) for transforms; use `asSequence()` for large collections with multiple chained operations** (avoids intermediate lists).

## Coroutines

11. **Structured concurrency:** launch inside a `CoroutineScope` tied to a lifecycle (`viewModelScope`, `lifecycleScope`, application scope). `GlobalScope` is banned without a written justification.
12. **suspend functions don't block:** wrap blocking I/O in `withContext(Dispatchers.IO)`. A suspend function should be safe to call from any dispatcher (main-safety convention).
13. **Don't swallow `CancellationException`** - a broad `catch (e: Exception)` in a coroutine must rethrow it, or cancellation breaks silently.
14. **`Flow` for streams, `StateFlow`/`SharedFlow` for observable state/events;** collect from the right scope, `flowOn` for upstream context.

## Ecosystem

15. **Match the project's Kotlin and coroutines versions** (`build.gradle.kts`) before using new stdlib APIs (e.g., `Enum.entries`, data objects, context receivers).
16. **Java interop: annotate for the other side** (`@JvmStatic`, `@JvmOverloads`) when Java consumes your Kotlin, and treat platform types (`String!`) from Java as nullable until proven otherwise.
