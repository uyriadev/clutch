# React

## Component and state design

1. **State lives at the lowest component that needs it.** Lift only when siblings genuinely share it; reach for context only for true cross-cutting data (theme, auth, locale) - context is not a state-management system for frequently-changing data (every consumer re-renders).
2. **Derive, don't duplicate.** If a value can be computed from props/state during render (`const fullName = first + last`), compute it - don't mirror it into state and sync with an effect. Duplicated state is the root of most React bugs.
3. **Never mutate state.** New objects/arrays on every update (`setItems([...items, x])`, or produce with a library the project uses). Mutation "works" until a memoized child doesn't re-render.
4. **Functional updates when the next state depends on the previous:** `setCount(c => c + 1)` - the closure-captured value is stale in async callbacks and batched updates.
5. **Components are pure during render:** no side effects, no mutation of external variables, no `Date.now()`/`Math.random()` in the render path where it breaks consistency (StrictMode double-render will expose you).

## Effects - the most misused API

6. **`useEffect` is for synchronizing with external systems** (subscriptions, DOM APIs, network in non-framework code) - not for responding to state changes. "When X changes, update Y" is derived state or an event handler, not an effect.
7. **Complete dependency arrays, honestly.** Don't silence the exhaustive-deps lint - restructure instead (move functions inside the effect, use functional updates, extract stable values). A lied-about dependency array is a stale-closure bug on a timer.
8. **Every subscribing effect returns a cleanup.** Listeners, intervals, observers, aborted fetches (`AbortController`). StrictMode mount-unmount-mount exists to catch you skipping this.
9. **Data fetching belongs to the framework or a query library** (React Query/SWR, or the meta-framework's loader) in any real app - hand-rolled fetch-in-effect lacks caching, dedup, race handling, and revalidation.

## Lists, keys, memoization

10. **Keys are stable identities, never array indexes** for lists that reorder, insert, or delete - index keys cause state to stick to the wrong item.
11. **Memoize for measured problems, not as ritual.** `memo`/`useMemo`/`useCallback` add complexity and only help when referential stability actually prevents re-renders - and they're moot under React Compiler. Profile first.
12. **Custom hooks to share stateful logic** (`useDebounce`, `usePagination`); components to share UI. A 300-line component with six `useState`s wants a reducer or decomposition.

## Ecosystem hygiene

13. **Controlled or uncontrolled inputs - pick one per field and don't flip** (that warning means a `value` went from `undefined` to defined; initialize state to `''`).
14. **Accessibility is part of the component:** semantic elements inside, labels wired to inputs, keyboard paths for custom widgets, focus management in modals (or use a headless UI library that does it).
15. **Respect the project's React version and paradigm:** Server Components/`use client` boundaries in modern Next.js, hooks-only in most codebases, no new class components ever.
