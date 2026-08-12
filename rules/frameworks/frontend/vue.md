# Vue 3

1. **Composition API with `<script setup>` for new code** (unless the codebase is Options API - then match it; don't mix styles in one component).
2. **Reactivity rules that bite:** don't destructure props or reactive objects (loses reactivity - use `toRefs`/`computed`); `ref` for primitives and things you'll reassign, `reactive` for object graphs you'll mutate in place; remember `.value` in script (templates auto-unwrap).
3. **`computed` for anything derivable** - never a `watch` that copies state A into state B. Computed properties must be pure: no side effects, no async, no mutation inside.
4. **`watch` for genuine side effects on change** (fetch, imperative APIs); prefer explicit sources over `watchEffect`'s implicit tracking when the trigger matters; clean up with `onWatcherCleanup`/return-cleanup, and mind `immediate`/`deep` costs (deep-watching large trees is a perf tax).
5. **Props down, events up:** props are readonly - never mutate one; emit events declared with `defineEmits`, model two-way state with `defineModel`/`v-model`. Reaching into `$parent` or mutating a prop object's fields is a hidden-coupling bug even when it "works."
6. **`v-for` needs a stable `:key`** (never index for reorderable lists); never `v-if` on the same node as `v-for` (precedence changed between Vue 2 and 3 - nest or compute a filtered list instead; the computed is better anyway).
7. **Composables (`useX`) for shared stateful logic:** take refs/getters as arguments, return refs, register lifecycle hooks synchronously at the top level. Module-level shared `ref`s in a composable are global state - deliberate choice only (and SSR-unsafe).
8. **Pinia for app-level state** (not Vuex for new work, not a mesh of provide/inject): stores for cross-view domain state, component state for the rest. `storeToRefs` when destructuring stores.
9. **Template hygiene:** complex expressions go in computeds, not inline in the template; `v-html` only with sanitized content; attribute fallthrough understood when wrapping native elements (set `inheritAttrs: false` + explicit `v-bind="$attrs"` on wrappers).
10. **Lifecycle in Composition API terms:** `onMounted` for DOM/browser APIs, `onUnmounted` cleanup paired at declaration; async setup needs `<Suspense>` - otherwise fetch in `onMounted` or a composable/query library.
11. **TypeScript: type props/emits via the generic signatures** (`defineProps<{...}>()` with `withDefaults`), not runtime-only declarations, in TS codebases.
12. **Check Vue minor version for newer APIs** (`defineModel` 3.4+, Vapor/`onWatcherCleanup` 3.5+) - and whether the project is actually Vue 2 (Options API, different reactivity) before writing anything.
