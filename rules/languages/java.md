# Java

## Modern Java first

1. **Know the project's Java version before writing code** (check `pom.xml`/`build.gradle`). Use records, `var`, switch expressions, text blocks, and pattern matching where the version allows - but never above the project's target.
2. **Records for immutable data carriers;** hand-rolled getter/setter/equals/hashCode classes only when mutation or inheritance is genuinely required.
3. **`Optional` as a return type for "may be absent" - never as a field or parameter.** And never call `.get()` without a presence check; use `orElse`, `orElseThrow`, `map`.

## Nulls and immutability

4. **Attack null at the boundary:** validate parameters early (`Objects.requireNonNull` with a message), return empty collections instead of null, use `Optional` returns. Respect the project's annotations (`@Nullable`/`@NonNull`) if present.
5. **Immutable by default:** `final` fields, `List.of`/`Map.of` or `Collections.unmodifiable*` for exposed collections, defensive copies of mutable arguments you store. Shared mutable state is where Java concurrency bugs live.
6. **`equals`/`hashCode` travel together,** and must be consistent with use in `HashMap`/`HashSet`. Records give you this free - another reason to use them.

## Exceptions and resources

7. **try-with-resources for everything `AutoCloseable`.** Manual `finally { close() }` is legacy.
8. **Unchecked exceptions for programming errors, checked (sparingly) for recoverable conditions the caller must handle.** Never catch `Exception` broadly except at a top-level handler, and never swallow: log or rethrow with context (`throw new X(msg, cause)` - keep the cause).
9. **Don't use exceptions for control flow** - they're expensive to construct (stack traces) and hide logic.

## Collections and streams

10. **Program to interfaces:** `List`, `Map`, `Set` in signatures; the implementation is a construction detail.
11. **Streams for straightforward pipelines; loops for complex logic, early exit, or index math.** A stream with side-effect-laden `forEach` and stateful lambdas is worse than the loop it replaced.
12. **Choose implementations deliberately:** `ArrayList` default, `LinkedList` almost never, `HashMap` default, `ConcurrentHashMap` (not `synchronizedMap`) under concurrency, `EnumMap`/`EnumSet` for enum keys.

## Concurrency

13. **Executors and higher-level constructs over raw `Thread`.** Virtual threads (21+) for high-concurrency I/O where available.
14. **Every shared mutable field needs a stated synchronization story:** confinement, `volatile` (visibility only!), locks, atomics, or immutability. "It seems to work" is not a story.
15. **`CompletableFuture` chains must handle failure** (`exceptionally`/`handle`) - a dropped exceptional future is a silent failure.

## Ecosystem hygiene

16. **Respect the build tool and its conventions** - dependency versions come from the build file (and BOMs), not copy-pasted latest-versions from memory.
17. **Constructor injection over field injection** in DI frameworks - final fields, testable without the container.
