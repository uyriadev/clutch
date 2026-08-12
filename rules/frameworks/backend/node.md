# Node.js Backend - Express / Fastify / NestJS

## Runtime fundamentals (any framework)

1. **Never block the event loop.** No `*Sync` fs/crypto calls in request paths, no CPU-heavy loops inline - one blocked tick stalls every concurrent request. Offload CPU work to worker threads or a queue.
2. **Every async error must reach the error handler.** Unhandled promise rejections crash modern Node. In Express 4, async route errors need `next(err)` or a wrapper (Express 5 forwards them); Fastify and Nest handle async natively - know which you're in.
3. **Config from environment, validated at boot:** parse `process.env` once through a schema (zod/envalid) into a typed config object; crash at startup on missing config, not at first use at 3am.
4. **Graceful shutdown:** trap SIGTERM, stop accepting connections, drain in-flight requests, close DB pools/queues, then exit. Containers get ~10s - use them.
5. **Structured logging (pino or the house logger) with request correlation** - no `console.log` in request paths; redact tokens/PII at the logger config level.

## HTTP layer

6. **Validate every input at the edge:** body, query, params, headers - schema-validated (zod / Fastify's JSON schema / Nest's ValidationPipe with `whitelist: true`) before any logic touches them. Types alone check nothing at runtime.
7. **Route handlers are thin:** parse/validate -> call service function -> map result to status/body. Business logic lives in plain, framework-free modules - testable without HTTP.
8. **Correct status codes and consistent error shape:** one error-handling middleware/filter produces `{ error: { code, message } }`-style responses; internal details go to logs, generic messages to clients. 4xx for caller mistakes, 5xx for yours.
9. **The standard hardening set:** helmet (headers), CORS as an explicit allowlist, rate limiting on auth/expensive endpoints, body size limits, cookie flags (`httpOnly`, `secure`, `sameSite`).

## Framework-specific

10. **Express: middleware order is the program.** Body parsing -> auth -> routes -> 404 -> error handler (4-arg signature, last). Anything after `res.send` still runs - `return` your responses.
11. **Fastify: work with the plugin model.** Encapsulation contexts, decorators typed via declaration merging, schemas on every route (they're also serialization speedups), hooks over ad-hoc middleware.
12. **NestJS: respect the architecture you bought.** DI everywhere (no `new Service()` in code), modules with explicit imports/exports, DTOs with class-validator, guards for auth / pipes for validation / interceptors for cross-cutting / filters for errors - don't smuggle Express habits into request handlers.

## Data and jobs

13. **One shared DB pool sized deliberately;** parameterized queries or the ORM (see the ORM rules); every external call gets a timeout and an abort path - a hung upstream with no timeout is an outage multiplier.
14. **Anything slower than ~a second doesn't belong in a request:** queue it (BullMQ etc.), return 202/status endpoint. Retries with backoff + idempotency keys on the consumer side.
