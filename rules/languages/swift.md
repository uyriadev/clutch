# Swift

## Optionals and value types

1. **Force-unwraps (`!`) are near-banned:** acceptable only for programmer-error invariants (IBOutlets, resources guaranteed in the bundle) where crashing is the correct response. Everywhere else: `if let`/`guard let`, `??`, optional chaining.
2. **`guard let` for early exit;** keep the happy path unindented. `guard` communicates "this must hold to proceed" - use it for preconditions.
3. **Structs and enums by default; classes when you need identity or reference semantics.** Value semantics eliminate whole categories of shared-mutation bugs.
4. **`let` over `var` everywhere possible** - for locals, properties, and captured values.
5. **Model states as enums with associated values** (`case loaded(Data)`, `case failed(Error)`), not booleans + optionals that permit impossible combinations. Switch exhaustively; avoid `default` on enums you own.

## Errors and API design

6. **`throws`/`do-catch` for recoverable failures; `Result` when the error travels as a value; `fatalError`/preconditions for impossibilities.** Never `try?` away an error you should handle or log - silent nil-on-failure hides bugs.
7. **Protocol-oriented where it earns its keep:** protocols for behavior contracts and testability seams, not a protocol per class as ritual.
8. **Follow Swift API Design Guidelines naming:** methods read as phrases at the call site (`items.insert(x, at: 0)`), argument labels doing grammatical work, no Objective-C-style prefixes.

## Concurrency (modern Swift)

9. **Structured concurrency first:** `async/await`, `async let`/`TaskGroup` for parallelism. Unstructured `Task {}` needs a lifecycle answer (who cancels it?).
10. **UI state is `@MainActor`.** Annotate view models/UI-touching classes rather than sprinkling `DispatchQueue.main.async`.
11. **Respect Sendable and actor isolation** - with strict concurrency checking (Swift 6 mode), these are compile errors; don't paper over them with `@unchecked Sendable` unless you can state the invariant that makes it safe.
12. **Check for cancellation in long tasks** (`Task.checkCancellation()`), and honor it downstream.

## Memory and platform

13. **`[weak self]` in escaping closures stored by the object they capture** (retain cycles); `guard let self` inside. Delegates are `weak var`. Not every closure needs `weak` - non-escaping and short-lived ones don't.
14. **Check the minimum deployment target before using new APIs;** wrap newer calls in `if #available` with a real fallback.
15. **Codable for serialization with explicit `CodingKeys` when names differ;** date/key strategies configured on the coder, not hand-rolled.
