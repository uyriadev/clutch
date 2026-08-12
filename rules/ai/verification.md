# Verification Discipline

Rules for proving work is done, not just believing it.

## The core rule

1. **"Done" means verified, not written.** Code that compiles is not done. Code that looks right is not done. Done means you executed it (or its tests) and observed the expected behavior. If you cannot run it, say "written but unverified" - never imply otherwise.

## Running and testing

2. **Run the narrowest relevant check first, then widen.** One test file before the suite, one endpoint before the integration run. Fast feedback loops catch mistakes while context is fresh.
3. **Run the actual failing case.** When fixing a bug, re-run the exact reproduction that demonstrated it - not a nearby test that happens to pass.
4. **A new test must fail before the fix and pass after.** A test that passes against the broken code proves nothing. Verify the failure mode is captured.
5. **Check for regressions beyond the target.** After the targeted check passes, run the broader suite for the area you touched. Fixing one thing by breaking another is a net negative.
6. **Lint and typecheck before declaring completion** if the project has those tools configured. They're part of the definition of done, not optional extras.

## Honest reporting

7. **Report failures verbatim.** If tests fail, show the actual output. Never summarize a failure as "mostly passing" or bury it under successes.
8. **Never weaken a check to make it pass.** Deleting an assertion, widening a type to `any`, raising a timeout, or skipping a test to get green is falsifying evidence. If a check seems wrong, say why and ask - don't silently neuter it.
9. **Say what you skipped.** If you didn't run the E2E suite, couldn't test on the target platform, or mocked a dependency, list it. The gap between "verified" and "assumed" must always be visible to the user.
10. **Flaky is not passing.** If a test passes on retry, that's a finding to report, not a success to move past.

## Verifying claims about the environment

11. **Check versions and configs directly** (lockfiles, `--version`, config files) instead of assuming from memory. Training-data knowledge of library APIs is stale by default.
12. **When behavior contradicts documentation, trust the behavior** - then figure out why the docs disagree (wrong version? wrong config?) before proceeding.
13. **Absence of an error is not presence of correctness.** Silent completion of a data migration, a deploy, or a batch job requires positive confirmation: row counts, health checks, spot-checked output.
