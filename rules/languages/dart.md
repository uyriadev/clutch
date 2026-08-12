# Dart

1. **Sound null safety is the law:** no `!` without a stated invariant; prefer `?.`, `??`, pattern-based null checks. `late` only for genuinely deferred initialization you can prove happens-before-use - a `late` that throws is a hidden nullable.
2. **`final` by default** for locals and fields; `const` for compile-time constants and constructors (big win in Flutter rebuilds).
3. **Use modern Dart 3 features where the SDK constraint allows** (check `pubspec.yaml`): records for lightweight multi-returns, sealed classes + exhaustive `switch` expressions for state modeling, pattern matching/destructuring.
4. **Async:** `Future` chains as `async/await`; never drop a Future - await it or hand it to something that tracks it (`unawaited()` from `dart:async` makes intent explicit). `Stream` for sequences; cancel subscriptions in `dispose`.
5. **Errors:** throw `Error` subtypes for programmer mistakes, `Exception` types for recoverable conditions; `on SpecificException catch` over bare `catch`; always rethrow or handle - an empty catch is a bug.
6. **Collections:** spreads and collection-`if`/`for` (`[...a, if (x) b]`) over imperative buildup; typed literals (`<String>[]`) where inference can't see the type.
7. **Naming and style per Effective Dart:** `lowerCamelCase` members, `UpperCamelCase` types, `snake_case` files; `dart format` output unedited; fix `dart analyze` findings rather than ignoring them (`// ignore:` needs a reason).
8. **Constructors:** named constructors for alternate creation paths, initializing formals (`this.x`), `required` named parameters over long positional lists.
9. **Prefer composition + small classes;** mixins for genuine cross-cutting reuse, not inheritance ladders.
10. **Isolates for CPU-heavy work** (`compute`/`Isolate.run`) - the main isolate shares the UI thread in Flutter; JSON-decoding a huge payload on it janks frames.
