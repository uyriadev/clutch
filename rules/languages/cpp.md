# C++

## Ownership - RAII or nothing

1. **No naked `new`/`delete` in application code.** `std::unique_ptr` by default, `std::shared_ptr` only for genuinely shared lifetime (it's a design statement, not a convenience), `make_unique`/`make_shared` to construct.
2. **Raw pointers and references mean "borrowed, non-owning"** - fine for parameters that observe. A function taking `T*` must document lifetime expectations; never store a borrowed pointer beyond the call without a lifetime argument.
3. **Rule of zero:** write no destructor/copy/move if members manage themselves. If you must write one of the five, deal with all five (`= default`/`= delete` explicitly).
4. **RAII for every resource** - files, locks (`std::lock_guard`/`scoped_lock`), timers, handles. If cleanup lives in a manually-called function, it will eventually be skipped by an early return or exception.

## Correctness idioms

5. **`const` correctness throughout:** member functions, parameters (`const T&` for read-only non-trivial types), locals. Pass small trivial types by value.
6. **Prefer values and moves over pointer webs.** `std::move` when transferring ownership; never use a moved-from object except to assign/destroy it.
7. **Initialize at declaration; brace initialization to avoid narrowing.** Beware the most vexing parse; `auto` where the type is obvious or spelled on the right.
8. **`std::string_view`/`std::span` for non-owning views in parameters** - and never return or store a view of a temporary (classic dangling bug: `string_view sv = s + "x";`).
9. **Know your standard** (check CMake `CXX_STANDARD`): C++17 minimum assumptions, C++20 (`ranges`, concepts, `format`) only if the project targets it.

## The standard library is the default

10. **Algorithms over hand loops where they name the intent:** `find_if`, `any_of`, `transform`, `sort` + `unique`. Containers: `vector` unless proven otherwise; `unordered_map` for lookup; reserve when size is known.
11. **`std::optional` for maybe-values, `std::variant` + `std::visit` for closed alternatives,** instead of magic sentinels and type-flag structs.
12. **Exceptions or error codes - follow the codebase's choice consistently.** If exceptions: constructors may throw, destructors never; `noexcept` on moves. If no exceptions (games/embedded): check the returns, use `expected`-style types.

## Sharp edges

13. **UB rules from C apply** (see c.md), plus: iterator/reference invalidation (a `push_back` can invalidate everything pointing into the vector), dangling lambda captures (`[&]` escaping the scope), ODR violations.
14. **Capture deliberately in lambdas that outlive the scope:** by value/`[x = std::move(x)]`, never `[&]` into a stored callback or thread.
15. **Concurrency:** `std::jthread`/`thread` with clear join points, data protected by mutexes or passed by ownership, `std::atomic` for flags - and TSan/ASan/UBSan in CI.
16. **Headers:** `#pragma once` or guards per convention, include-what-you-use, no `using namespace std;` at namespace scope in headers, forward-declare where sufficient to cut compile times.
