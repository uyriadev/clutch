# Go Web Services - net/http, Gin, Echo, chi

1. **Go language rules apply first** (see go.md) - errors wrapped with context, goroutine lifecycles owned, `context.Context` honored. Web specifics below.
2. **Prefer the standard library baseline:** modern `net/http` (1.22+ ServeMux has method+path patterns) covers more than memory suggests; Gin/Echo/chi are fine when the project uses them - match the router that's there, don't add a second.
3. **`r.Context()` flows through everything:** DB queries, HTTP calls, downstream services - so client disconnects and timeouts propagate. Never `context.Background()` inside a handler chain except for work that must outlive the request (and that gets its own timeout and ownership).
4. **Servers get real timeouts:** `ReadTimeout`, `WriteTimeout`, `IdleTimeout`, `ReadHeaderTimeout` on `http.Server` (defaults are infinite - a slowloris gift); `http.MaxBytesReader` on bodies; outbound clients get `Timeout` too (the zero-value `http.Client` never times out).
5. **Graceful shutdown is standard equipment:** catch SIGTERM, `srv.Shutdown(ctx)` with a deadline, drain background workers, close pools.
6. **Handlers: decode -> validate -> service call -> encode.** JSON decoding checks errors and rejects unknown fields where the contract demands (`DisallowUnknownFields`); validation explicit (validator library or hand-rolled - either way before logic); responses via a single respond/error helper for consistent shape and correct status codes.
7. **Don't forget the write path errors:** `json.NewEncoder(w).Encode` errors are usually ignorable-but-logged; setting status after writing body is a silent bug (`WriteHeader` once, before body).
8. **Middleware for cross-cutting only** (logging with request IDs, recovery, auth, CORS allowlist, rate limits) - composed in one visible chain; per-route auth still checks resource ownership in the handler/service (token != permission).
9. **Dependencies via struct fields, not globals:** handlers are methods on a server/handler struct holding the DB pool, logger, clients - testable with real constructors. No `var db *sql.DB` package globals in new code.
10. **Database: one `sql.DB`/pgx pool sized deliberately, parameterized queries always, `rows.Close()`/`rows.Err()` checked, transactions via helper that commits/rolls back on error path** - see sql.md for query rules.
11. **Concurrency in handlers is deliberate:** fan-out with `errgroup.WithContext`, never spawn unsupervised goroutines writing to the ResponseWriter (invalid after handler returns), share nothing without a mutex.
12. **Tests: `httptest.NewServer`/`httptest.NewRecorder` with table-driven cases,** real router wiring under test, Testcontainers or a test DB for storage - the handler-through-router path is cheap to test in Go; use it.
