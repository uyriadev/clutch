# Code Rules

A comprehensive, drop-in collection of coding rules for AI assistants - covering universal AI working discipline, major languages, frameworks, databases, testing, and devops. Each file is self-contained and written as direct, actionable rules (not tutorials), so any subset can be composed into a `CLAUDE.md`, Cursor rules, system prompt, or team style guide.

## How to use

- **Per-project:** copy (or reference) the AI docs plus only the language/framework files that match the project's stack. A React + FastAPI + Postgres app needs ~6 files, not 60.
- **Always include the `ai/` set** - those are stack-agnostic and highest-leverage.
- **Layering:** `ai/` (how to work) -> `languages/` (how to write the language) -> `frameworks/` (how to use the stack) -> `databases/`/`testing/`/`devops/` as applicable. Framework files assume their language file; e.g. `react.md` assumes `typescript.md`.
- Files deliberately repeat one theme: **verify against the installed version - training-data knowledge of APIs is stale by default.**

## AI working discipline (`ai/`) - include always

| File | Covers |
|---|---|
| [reasoning.md](ai/reasoning.md) | Think before coding, hypothesis-driven debugging, depth calibration, conclusive endings |
| [verification.md](ai/verification.md) | "Done" = verified; honest reporting; never weaken checks to pass |
| [scope-control.md](ai/scope-control.md) | Do all of what was asked, only what was asked; when to stop and ask |
| [code-quality.md](ai/code-quality.md) | Naming, comments, error handling, dead code, dependencies - language-agnostic |
| [security.md](ai/security.md) | Secrets, injection family, authz, headers, dependency hygiene |
| [performance.md](ai/performance.md) | N+1s, accidental quadratics, caching honesty, measure-first |
| [context-efficiency.md](ai/context-efficiency.md) | Search-then-read, no re-derivation, right-sized exploration |

## Languages (`languages/`)

Core: [typescript](languages/typescript.md) - [javascript](languages/javascript.md) - [python](languages/python.md) - [java](languages/java.md) - [csharp](languages/csharp.md) - [sql](languages/sql.md)

Systems: [c](languages/c.md) - [cpp](languages/cpp.md) - [rust](languages/rust.md) - [go](languages/go.md)

Mobile: [swift](languages/swift.md) - [kotlin](languages/kotlin.md) - [dart](languages/dart.md)

Scripting & other: [php](languages/php.md) - [ruby](languages/ruby.md) - [shell (bash + powershell)](languages/shell.md) - [lua](languages/lua.md)

Data & niche: [r](languages/r.md) - [scala](languages/scala.md) - [elixir](languages/elixir.md) - [zig](languages/zig.md)

Markup & config: [html-css](languages/html-css.md) - [config-formats (yaml/json/toml)](languages/config-formats.md)

## Frameworks (`frameworks/`)

**Frontend:** [react](frameworks/frontend/react.md) - [nextjs](frameworks/frontend/nextjs.md) - [vue](frameworks/frontend/vue.md) - [nuxt](frameworks/frontend/nuxt.md) - [angular](frameworks/frontend/angular.md) - [svelte/sveltekit](frameworks/frontend/svelte.md) - [astro](frameworks/frontend/astro.md) - [tailwind](frameworks/frontend/tailwind.md) - [shadcn-ui](frameworks/frontend/shadcn-ui.md)

**Backend:** [node (express/fastify/nest)](frameworks/backend/node.md) - [django](frameworks/backend/django.md) - [fastapi](frameworks/backend/fastapi.md) - [flask](frameworks/backend/flask.md) - [spring-boot](frameworks/backend/spring-boot.md) - [aspnet-core](frameworks/backend/aspnet-core.md) - [laravel](frameworks/backend/laravel.md) - [rails](frameworks/backend/rails.md) - [go-web](frameworks/backend/go-web.md) - [rust-web (axum/actix)](frameworks/backend/rust-web.md)

**Mobile:** [react-native](frameworks/mobile/react-native.md) - [flutter](frameworks/mobile/flutter.md) - [swiftui](frameworks/mobile/swiftui.md) - [jetpack-compose](frameworks/mobile/jetpack-compose.md)

**Desktop:** [electron & tauri](frameworks/desktop/electron-tauri.md)

**Data / ML / AI:** [pandas-numpy](frameworks/data-ml/pandas-numpy.md) - [pytorch](frameworks/data-ml/pytorch.md) - [tensorflow-keras](frameworks/data-ml/tensorflow-keras.md) - [scikit-learn](frameworks/data-ml/scikit-learn.md) - [llm-apps (SDKs, RAG, agents)](frameworks/data-ml/llm-apps.md)

## Databases (`databases/`)

[postgresql](databases/postgresql.md) - [mysql](databases/mysql.md) - [sqlite](databases/sqlite.md) - [mongodb](databases/mongodb.md) - [redis](databases/redis.md) - [orms (prisma/drizzle/sqlalchemy/ef)](databases/orms.md)

Language-level SQL rules live in [languages/sql.md](languages/sql.md); the database files build on it.

## Testing (`testing/`)

[testing-principles](testing/testing-principles.md) (framework-agnostic - include with any of the below) - [js-unit-testing (jest/vitest)](testing/js-unit-testing.md) - [e2e-testing (playwright/cypress)](testing/e2e-testing.md) - [pytest](testing/pytest.md) - [jvm-dotnet-testing (junit/xunit/nunit)](testing/jvm-dotnet-testing.md)

## DevOps (`devops/`)

[docker](devops/docker.md) - [kubernetes](devops/kubernetes.md) - [terraform](devops/terraform.md) - [ci-cd (github actions + general)](devops/ci-cd.md)

## Design principles of this collection

1. **Rules, not lore.** Every line is an instruction an AI (or human) can act on, with the *why* kept to a clause.
2. **Weighted toward the actual failure modes** - the mistakes AI assistants and reviewers see repeatedly (N+1s, unawaited promises, leaked state, weakened tests, stale API knowledge), not textbook completeness.
3. **Convention-respecting.** Nearly every file's first rule is some form of "check what the project already does and match it" - because the most common AI failure isn't bad code, it's *foreign* code.
4. **Version-humble.** Frameworks change under any static document (including this one). Files teach the check ("read the lockfile first"), not just the current answer. Review yearly.
