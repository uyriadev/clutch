# Spring Boot

## Architecture

1. **Constructor injection, final fields, no `@Autowired` on fields.** Field injection hides dependencies and blocks plain-JUnit testing. One constructor = no annotation needed.
2. **Layers stay honest:** controllers translate HTTP <-> DTOs; services hold business logic and transactions; repositories touch data. Entities never cross the API boundary - DTOs (records) in and out, mapped explicitly (or MapStruct).
3. **Let Boot configure it:** starters + `application.yml` properties + `@ConfigurationProperties` (typed, validated) over hand-rolled `@Configuration` beans replicating auto-config. Secrets from env/vault, never in the YAML committed to git. Profiles for environment differences.

## Web layer

4. **Validate at the edge:** `@Valid` on request DTOs with constraint annotations; a `@RestControllerAdvice` exception handler mapping domain and validation errors to a consistent error body (ProblemDetail where adopted) and correct status codes - no stack traces in responses.
5. **Correct REST semantics:** 201 + Location on create, 204 for empty success, 404 via exception not null-returns, pagination (`Pageable`) on collection endpoints - never return unbounded lists.

## Persistence - where Spring apps actually break

6. **`@Transactional` on service methods defining the unit of work** - know the traps: it's proxy-based, so self-invocation (this.method()) bypasses it; it doesn't roll back on checked exceptions by default; keep transactions short and never call external services inside one.
7. **LazyInitializationException means the design leaked** - an entity escaped its session. Fix with fetch joins / `@EntityGraph` / DTO projections for the use case - not `FetchType.EAGER` (a global N+1 generator) and not Open-Session-in-View (disable `spring.jpa.open-in-view` on new services and fetch consciously).
8. **N+1 hunting is mandatory:** log SQL in dev, fetch collections explicitly per query, use projections (`interface` or record) for read paths that don't need managed entities. Derived query methods for simple lookups; `@Query` JPQL for anything with joins.
9. **Migrations via Flyway/Liquibase - `ddl-auto=validate` in production.** `update` is for prototypes only.

## Security and operations

10. **Spring Security config is code review priority #1:** explicit `SecurityFilterChain`, deny-by-default request matchers, method security (`@PreAuthorize`) for service-level rules, resource ownership checked against the principal - role checks alone don't stop IDOR.
11. **Actuator exposed deliberately:** health/metrics endpoints allowlisted, everything else locked; never ship `management.endpoints.web.exposure.include=*` to prod.
12. **External calls get timeouts, retries with backoff (spring-retry/resilience4j), and circuit breakers where they can cascade** - a default RestClient/WebClient with no timeout is an outage waiting upstream. Prefer `RestClient` (modern) over `RestTemplate` in new code.
13. **Async/scheduled work:** `@Async`/`@Scheduled` need configured executors (defaults are surprising), idempotent jobs, and - for real workloads - a queue/outbox, not an in-process scheduler.
14. **Tests in layers:** plain JUnit for services (constructor-injected mocks), `@WebMvcTest` for controllers, `@DataJpaTest` + Testcontainers for repositories (H2 lies about production SQL), full `@SpringBootTest` sparingly - it's the slow tier.
