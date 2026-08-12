# Svelte 5 / SvelteKit

## Which Svelte? - decide before writing a line

1. **Check the major version.** Svelte 5 runes (`$state`, `$derived`, `$effect`, `$props`) replace Svelte 3/4's implicit reactivity (`let` + `$:` + `export let`). The two dialects look similar and are not interchangeable - write the one the project uses.

## Svelte 5 idiom

2. **`$state` for reactive state, `$derived` for anything computable, `$effect` only for true side effects** (DOM, subscriptions, imperative libs). The React lesson applies verbatim: syncing state with effects is a design bug - derive it.
3. **`$props()` with destructuring + defaults; `$bindable()` only for genuinely two-way props.** Callback props (`onclick`-style) over `createEventDispatcher` (deprecated in 5).
4. **Snippets (`{#snippet}`/`{@render}`) replace slots** in new code; keep them small and typed.
5. **Deep reactivity is proxy-based:** `$state` objects/arrays track mutation - mutate freely in 5 (unlike React), but don't destructure reactive objects into plain locals and expect updates.
6. **`.svelte.ts` modules for shared reactive logic** (runes work there) - this largely replaces writable stores for app state; stores remain fine for existing code and library interop.

## Svelte 3/4 idiom (legacy codebases)

7. **Reactivity is assignment:** `arr.push(x)` doesn't trigger - `arr = [...arr, x]` does. `$:` for derived values and reactions; know it only re-runs when directly-referenced variables change.
8. **`export let` for props; stores (`writable`/`derived`) with `$store` auto-subscription** for shared state; manual `subscribe` needs `onDestroy` cleanup.

## SvelteKit (either Svelte version)

9. **Data loads in `load` functions:** `+page.server.ts` for anything touching secrets/DB, `+page.ts` for universal loads. Return serializable data; use the provided `fetch` (SSR-aware, deduped). Never fetch in component `onMount` for page data.
10. **Mutations are form actions** (`+page.server.ts` `actions`) with progressive enhancement (`use:enhance`) - validate input server-side, check auth in the action, return `fail(400, {...})` for form errors. API-shaped endpoints go in `+server.ts`.
11. **Secrets only in server modules:** `$env/static/private` in `*.server.ts` files - importing it client-side is a build error; keep it that way by not proxying secrets through page data.
12. **Know the file conventions:** `+layout` data flows to children, `+error.svelte` boundaries, `hooks.server.ts` for auth/middleware (`locals` for per-request context), route groups `(name)`. Don't rebuild what a convention file provides.
13. **SSR safety:** no `window`/`document` at module scope or during SSR - `browser` from `$app/environment`, or `onMount`. State in module scope on the server leaks across requests - per-request state lives in `locals` or load returns.
