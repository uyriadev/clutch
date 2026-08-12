# TypeScript

## Types

1. **`any` is forbidden; `unknown` is the escape hatch.** `unknown` forces narrowing before use. If you must interoperate with untyped code, confine the `any` to one boundary function with a typed signature.
2. **Let inference work.** Don't annotate what TypeScript already knows (`const x: string = "a"`). Do annotate function signatures - parameters and return types are documentation and error firewalls.
3. **Model alternatives as discriminated unions,** not optional-field grab-bags. `{ status: 'ok', data } | { status: 'error', error }` makes illegal states unrepresentable; `{ data?, error? }` invites the impossible combination.
4. **Derive types instead of duplicating them:** `keyof`, `typeof`, `ReturnType<>`, `Pick`/`Omit`, `as const`. Two hand-maintained copies of the same shape will drift.
5. **`interface` for object shapes that may be extended; `type` for unions, intersections, and everything else.** Pick one convention per codebase and stay consistent with what's there.
6. **Casting is a last resort in this order:** narrow with a type guard > fix the type at its source > `satisfies` > `as`. A cast (`as X`) silences the compiler without changing reality; double-casting (`as unknown as X`) is a bug report scheduled for later.
7. **Write type guards for runtime narrowing** (`function isUser(x: unknown): x is User`) and validate external data with a schema library (zod, valibot) at the boundary - TypeScript types are erased at runtime and check nothing.

## Strictness

8. **`strict: true` always;** prefer `noUncheckedIndexedAccess` on new projects (array/record access returns `T | undefined` - because it can be).
9. **Handle `null`/`undefined` where they enter.** Non-null assertions (`!`) require certainty the compiler lacks but you can justify; if you can't state why it's non-null in a half-line comment, handle the null.
10. **`enum` - prefer union types (`type Level = 'info' | 'warn'`) or `as const` objects.** They erase cleanly and don't have the numeric-enum reverse-mapping quirks.

## Idioms

11. **`readonly` and immutability by default:** `readonly` fields, `ReadonlyArray`/`readonly T[]` for parameters you don't mutate.
12. **Narrow error types in catch:** caught values are `unknown` - check `instanceof Error` before touching `.message`.
13. **Exhaustiveness-check unions** with a `never` default branch (`const _exhaustive: never = value`) so adding a variant breaks the build instead of silently falling through.
14. **Avoid `@ts-ignore`; use `@ts-expect-error` with a reason comment** if suppression is truly needed - it self-destructs when the error disappears.
