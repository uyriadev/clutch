# Angular (modern, v16+)

1. **Check the Angular major first - the framework changed shape.** Standalone components (default 17+), signals, new control flow (`@if`/`@for`), `inject()` function, zoneless change detection are modern idiom; NgModule-heavy code is legacy pattern. Write to the project's version and style.
2. **Standalone components + `inject()` for new code** in modern projects: no new NgModules; dependencies via `inject(Service)` in field initializers or constructor DI per house style.
3. **Signals for component state** (v17+ projects): `signal`/`computed`/`effect`, `input()`/`output()`/`model()` over decorator equivalents where adopted. Derive with `computed`, never mirror state and sync with `effect` - effects are for side effects (DOM, logging), not state propagation.
4. **RxJS discipline where observables live** (HTTP, router, forms): pipe operators over nested subscribes; **every subscription has a death plan** - `async` pipe (preferred), `takeUntilDestroyed()`, or explicit teardown. `switchMap` for latest-wins requests (typeahead), `concatMap`/`exhaustMap`/`mergeMap` chosen deliberately, not by habit.
5. **`async` pipe / signal reads in templates over manual `.subscribe()` + field assignment** - no `subscribe` inside components for data that just renders.
6. **New control flow (`@if`, `@for` with mandatory `track`) in v17+ templates;** `trackBy` in legacy `*ngFor`. Untracked loops over changing lists are Angular's classic perf hole.
7. **`OnPush` change detection (or zoneless/signals) for components,** with immutable inputs - mutating an `@Input` object and wondering why the view didn't update is the corresponding classic bug.
8. **Reactive forms with typed form controls** (`FormGroup<...>`, `NonNullableFormBuilder`) for real forms; template-driven only for trivia. Validators composed, error states rendered accessibly.
9. **Services for logic and state, components for presentation:** `providedIn: 'root'` singletons by default; component-scoped providers deliberately. HTTP through a typed data service layer + interceptors (auth, errors) - never `fetch` scattered in components.
10. **Router conventions:** lazy-load feature routes (`loadComponent`/`loadChildren`), functional guards/resolvers (`CanActivateFn`), route-level `inject()` - class guards are legacy.
11. **Lifecycle and DI correctness:** cleanup in `ngOnDestroy`/`DestroyRef`; no DOM access before `afterNextRender`/`AfterViewInit`; `ExpressionChangedAfterItHasBeenChecked` means you mutated state during change detection - restructure, don't `setTimeout` it away.
12. **Testing with `TestBed` (or the project's chosen shallow-render library), HttpTestingController for HTTP** - and keep components thin enough that logic tests live in plain service specs.
