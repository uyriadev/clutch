# C#

## Modern C# baseline

1. **Check the target framework and `LangVersion` first** (`.csproj`). Use file-scoped namespaces, records, pattern matching, collection expressions, and primary constructors where the version allows.
2. **Nullable reference types on (`<Nullable>enable</Nullable>`) and warnings respected.** `!` (null-forgiving) requires a justification you could state in a comment; fixing the nullability is better.
3. **Records for immutable data; `init` setters and `required` members over constructor telescoping.** `with` expressions for non-destructive mutation.

## Async - where C# reviews are won and lost

4. **`async` all the way down.** Never block on async code (`.Result`, `.Wait()`, `.GetAwaiter().GetResult()`) - that's a deadlock in UI/legacy-ASP.NET contexts and thread starvation elsewhere.
5. **`async void` only for event handlers.** Everything else returns `Task`/`Task<T>`/`ValueTask`.
6. **Accept and pass `CancellationToken`** through async call chains; hand it to everything that takes one.
7. **`ConfigureAwait(false)` in library code;** don't bother in ASP.NET Core apps (no sync context) - match the project's convention.
8. **A returned `Task` is never dropped.** Fire-and-forget requires an explicit pattern (background service, logged continuation), not a discarded call.

## Idioms

9. **Properties over public fields; expression-bodied members where they aid brevity, not cleverness.**
10. **`IEnumerable<T>` parameters, concrete/`IReadOnlyList<T>` returns as sensible.** Beware multiple enumeration of `IEnumerable` - materialize (`ToList`) when you'll iterate twice.
11. **LINQ for queries, loops for algorithms.** Same rule as streams in Java: stateful lambdas and side effects inside LINQ chains are a smell. Know deferred execution: the query runs when enumerated, not when written.
12. **`using` declarations for `IDisposable`;** implement `IAsyncDisposable` where cleanup is async.
13. **Pattern matching (`switch` expressions, `is` patterns) over cascading if/else-if type checks.** Exhaustive switches with a discard arm that throws.
14. **String handling:** interpolation (`$""`) by default; `StringBuilder` in loops; `string.Equals(x, y, StringComparison.OrdinalIgnoreCase)` over `ToLower()` comparisons.

## Ecosystem

15. **Exceptions: specific types, with the original as `innerException` when wrapping.** Don't catch-and-rethrow with `throw ex;` (resets the stack trace) - use `throw;`.
16. **DI via constructor injection; register with the correct lifetime.** A singleton depending on a scoped service is a classic runtime bug - the container will tell you, listen to it.
17. **`DateTimeOffset` over `DateTime` for moments in time;** `DateTime` only for calendar concepts. `TimeProvider`/abstraction for testable time.
