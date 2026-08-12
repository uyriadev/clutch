# Testing Principles (framework-agnostic)

## What to test

1. **Test behavior through public interfaces, not implementation.** A test that breaks when you rename a private method (behavior unchanged) is friction; a test that survives a rewrite of internals while catching real regressions is the asset. Assert on outputs and observable effects, not call sequences and internal state.
2. **Every test answers: what breaks if this fails?** Tests exist to catch specific mistakes. A test asserting `2 + 2 === 4` about your mock's return value tests the mock, not the code - the most common AI-written-test failure.
3. **Coverage of the paths that matter beats coverage percentage:** error paths, boundaries (empty, one, many, max, malformed), concurrency-sensitive spots, and the bug you just fixed (regression test that failed before the fix - always). 100% line coverage with happy-path-only assertions is decorative.
4. **The test pyramid is about feedback speed:** many fast unit tests on logic, fewer integration tests on wiring (real DB via containers over mocked repositories - mocks of the database test your assumptions, not the database), few E2E tests on critical user journeys. Invert it and CI takes an hour and flakes.

## How to write them

5. **Arrange-Act-Assert, one behavior per test, named as a sentence:** `rejects_expired_tokens` / `"returns 404 when the order belongs to another user"` - a failing test's name should diagnose without reading the body.
6. **Tests are independent and order-free:** no shared mutable state, no reliance on execution order, own their setup (factories/builders over sprawling shared fixtures - a fixture edited for test A silently changes what test B tests).
7. **Determinism is non-negotiable:** control time (inject clocks/fake timers), seed or eliminate randomness, no real network, no sleeps - await conditions, not durations. A flaky test is a bug: fix it or delete it; retry-until-green normalizes ignoring the alarm.
8. **Mock at boundaries you own the contract for** (external APIs, payment providers, mail) - not your own internals. Over-mocked tests pass forever while production burns. Prefer fakes (in-memory implementations) over interaction-verifying mocks where possible.
9. **Assert specifically:** the expected value, not `isNotNull`; the error type and message contract, not "throws"; the relevant fields, not deep-equality on objects where irrelevant churn causes noise. Snapshot tests only for genuinely stable output, reviewed on change like code.

## Discipline

10. **Test code is production code:** DRY-ish (helpers/builders yes, but clarity beats deduplication in tests - some repetition that makes each test self-contained is correct), refactored, deleted when the behavior it tested dies.
11. **Never weaken a test to make it pass** - no deleted assertions, widened tolerances, raised timeouts, or `.skip` to get green. If the test is wrong, fix it and say so; if the code is wrong, fix that. (See ../ai/verification.md - this is the falsifying-evidence rule.)
12. **New behavior arrives with its tests in the same change;** the failing-then-passing sequence is the proof the test works. Bug fixes arrive with the regression test that would have caught them.
