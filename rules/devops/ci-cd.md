# CI/CD - GitHub Actions & general pipeline practice

## Pipeline design (any CI system)

1. **Fast feedback first:** lint + typecheck + unit tests as the first parallel wave (minutes), integration/E2E after, deploy last - a 40-minute serial pipeline that fails on a lint error at minute 38 is process abuse. Cache dependencies (lockfile-keyed) and build artifacts between jobs.
2. **CI runs what developers run:** the pipeline invokes the same scripts/commands as local (`npm test`, `make check`) - pipeline-only bash embedded in YAML drifts from reality and can't be debugged locally.
3. **Every check is deterministic and required or it's noise:** flaky jobs get fixed or quarantined (not retried-until-green as policy); a required check that everyone force-merges past is worse than no check. Pin toolchain versions in the pipeline (the same rule as everywhere: no `latest`).
4. **Build once, promote the artifact:** the image/bundle that passed tests is byte-for-byte what deploys - rebuilding per environment reintroduces the untested-variance problem CI exists to kill.
5. **Deploys are boring by construction:** deploy from main only, gated by all checks, with health verification after and an automated (or one-command, rehearsed) rollback. Migrations run forward-compatible ahead of code (expand -> deploy -> contract); a deploy that can't roll back because the schema moved is a designed-in outage.

## GitHub Actions specifics

6. **Pin third-party actions to a full commit SHA** (`uses: some/action@<sha>` with a version comment) - tags are mutable; a hijacked action tag with your secrets in scope is the modern supply-chain attack. First-party `actions/*` at major-version pin is acceptable per repo policy.
7. **Least-privilege `permissions:` explicitly:** top-level `permissions: contents: read`, job-level grants for what each job needs (`id-token: write` for OIDC, `pull-requests: write` for commenters). The default token scope is a liability you opt out of.
8. **OIDC to cloud providers over long-lived secrets:** short-lived federated credentials for AWS/GCP/Azure deploys; remaining secrets in GitHub Secrets/environments - never in the YAML, never echoed (masking is best-effort, not a guarantee - don't print secret-derived values).
9. **`pull_request_target` and script injection are the two classic Actions holes:** `pull_request_target`/`workflow_run` with checkout of PR code = attacker code with secrets - don't, without expert review. Untrusted input (`github.event.*` titles, branch names, comments) never interpolates into `run:` directly - pass via `env:` and quote.
10. **Concurrency groups on deploys** (`concurrency: { group: deploy-prod, cancel-in-progress: false }`) so parallel merges don't race deployments; `cancel-in-progress: true` on PR CI to stop burning minutes on obsolete commits.
11. **Environments for anything production-shaped:** required reviewers/wait timers on the `production` environment, environment-scoped secrets - branch protection + environments is the approval system; hand-rolled "check the actor" steps are not.
12. **Matrix and reuse over copy-paste:** `strategy.matrix` for version/OS spreads, reusable workflows (`workflow_call`) / composite actions for repeated pipelines - twelve near-identical YAML files drift twelve ways. `timeout-minutes` on every job (default is six hours of runner billing per hung job).
13. **Artifacts and logs tell the failure story:** upload test reports/traces/screenshots on failure, structured job summaries (`$GITHUB_STEP_SUMMARY`) - a red X with no artifacts forces a local reproduction someone may not be able to do.
