# JavaScript

## Declarations and equality

1. **`const` by default, `let` when reassignment is required, `var` never.**
2. **`===`/`!==` always.** The only acceptable `==` is `x == null` to test null-or-undefined in one shot - and prefer explicit checks even there.
3. **Optional chaining and nullish coalescing over `&&`/`||` guards:** `a?.b ?? fallback`. Note `||` treats `0`, `''`, and `false` as missing - that's a classic bug; use `??` when only null/undefined should trigger the fallback.

## Async

4. **`async/await` over `.then()` chains;** mixing the two styles in one function is a readability foul.
5. **Never fire-and-forget a promise silently.** Every promise is awaited, returned, or explicitly handled with `.catch`. An unhandled rejection is a crash (Node) or a silent failure (browser).
6. **Independent async work runs concurrently:** `Promise.all` (fail-fast) or `Promise.allSettled` (collect all outcomes) - not sequential awaits.
7. **Beware `forEach(async ...)`** - it doesn't await anything. Use `for...of` with await, or `Promise.all(items.map(...))` for parallel.
8. **`await` inside loops is a decision, not an accident:** serial when order/rate matters, parallel otherwise. Say which you chose.

## Data handling

9. **Don't mutate what you don't own:** function arguments, shared objects, arrays passed in. Spread/`structuredClone`/immutable updates for anything crossing a boundary. Watch mutating array methods (`sort`, `reverse`, `splice`) - prefer `toSorted`/`toReversed` where the runtime allows.
10. **Use the right structure:** `Map` for keyed collections with non-string keys or frequent add/remove, `Set` for membership, plain objects for records with known shape.
11. **Number quirks are real:** `0.1 + 0.2 !== 0.3` (use integer cents for money), integers above `Number.MAX_SAFE_INTEGER` corrupt silently (use `BigInt`), `typeof NaN === 'number'` (use `Number.isNaN`).
12. **Dates: reach for a library (date-fns, Temporal when available) for anything beyond timestamps.** Native `Date` mutation, zero-indexed months, and implicit local-timezone parsing are bug factories. Store and transmit UTC ISO-8601; convert at display.

## Modules and structure

13. **ESM (`import`/`export`) for new code;** don't mix `require` and `import` in the same file. Know which module system the project actually uses before writing either.
14. **No default exports for multi-symbol modules;** named exports refactor, grep, and auto-import better.
15. **Modules shouldn't run side effects on import** (network calls, global mutations). Import-time work makes testing and tree-shaking miserable.
16. **Deep-clone consciously:** spread is shallow. `structuredClone` for real cloning; know that it drops functions.
