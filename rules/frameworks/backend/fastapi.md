# FastAPI

## Async correctness - the #1 FastAPI failure mode

1. **`async def` endpoints must not make blocking calls.** One `requests.get`, sync ORM query, or `time.sleep` inside an async endpoint stalls the entire event loop for all requests. Async endpoint -> async libraries (httpx, SQLAlchemy async, asyncpg) all the way down.
2. **Plain `def` endpoints are legitimate:** FastAPI runs them in a threadpool - correct choice when your stack is sync (classic SQLAlchemy). Don't mark endpoints `async` as decoration; choose per what the body actually calls.
3. **CPU-bound work goes to a process pool or task queue,** not either kind of endpoint.

## Pydantic is the contract layer

4. **Every request body, and response, has a Pydantic model.** `response_model` (or return-type annotation) on every route - it validates, filters, and documents. Separate `UserCreate` / `UserUpdate` / `UserOut` models; never return ORM objects raw (leaks fields, breaks the schema).
5. **Validate at the model, not in the endpoint:** field constraints (`Field(ge=0, max_length=...)`), custom validators, enums for closed sets. Endpoint bodies should receive already-valid data.
6. **Pydantic v1 vs v2 check** (`model_dump` vs `.dict()`, `field_validator` vs `validator`, `ConfigDict`) - read the installed version before writing model code.

## Dependency injection is the architecture

7. **`Depends()` for everything shared:** DB sessions, current user, pagination params, settings. Yield-dependencies for anything needing cleanup (session per request: yield, then close). Don't create sessions ad hoc inside endpoints.
8. **Auth is a dependency chain:** `get_current_user` -> `get_current_active_user` -> role/permission checks, reused across routers. Per-resource ownership still gets checked against the loaded object - a valid token is not authorization.
9. **Settings via `pydantic-settings` `BaseSettings`,** injected as a (cached) dependency - not `os.getenv` scattered through modules.

## Structure and HTTP semantics

10. **Routers per domain (`APIRouter`), thin endpoints, logic in service functions** that don't import FastAPI. Prefix/tags/dependencies set at router level.
11. **Raise `HTTPException` with accurate status codes** (401 vs 403 vs 404, 422 comes free from validation); consistent error shape via exception handlers for domain errors. Set `status_code=201` on creation, 204 for empty success.
12. **Response streaming for large payloads** (`StreamingResponse`), `BackgroundTasks` only for fire-and-forget trivia - real jobs go to a queue (arq/Celery); lifespan context (not deprecated startup events) for pools and clients.
13. **The generated OpenAPI is a deliverable:** operation summaries, examples, and correct schemas - if `/docs` looks wrong, the API is wrong.
14. **Tests: `TestClient` (sync) or `httpx.AsyncClient` + `ASGITransport` (async), dependency overrides (`app.dependency_overrides`) for DB/auth** - not monkeypatching internals.
