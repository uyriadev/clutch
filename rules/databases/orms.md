# ORMs - Prisma, Drizzle, SQLAlchemy, Entity Framework, and kin

## Universal ORM rules

1. **An ORM abstracts the syntax, not the database.** You still owe: knowing what SQL your code emits (turn on query logging in dev), indexes matching your queries, and transaction boundaries. "The ORM handles it" is how N+1s and table scans ship.
2. **N+1 is the universal ORM bug - kill it explicitly per tool:** Prisma `include`/nested `select`, Drizzle `with`, SQLAlchemy `selectinload`/`joinedload`, EF `Include`/projection, ActiveRecord `includes`, Django `select_related`/`prefetch_related`. Any loop touching a lazy relation is guilty until query-logged innocent.
3. **Select what you need:** field/column selection (`select`, `only`, projections to DTOs) on hot read paths - hydrating full entities with relations to render three fields is memory and wire waste.
4. **Migrations come from the migration tool, reviewed as code:** generated diffs inspected before commit (autogeneration misses renames - it sees drop+add), never `db push`/`create_all`/`ddl-auto=update` against production, destructive changes flagged loudly, and schema constraints (unique, FK, not-null) live in the database - validation layers race; constraints don't.
5. **Transactions are explicit units of work:** wrap multi-write invariants in the ORM's transaction API (Prisma `$transaction`, SQLAlchemy `begin()`, EF's implicit `SaveChanges` unit +/- explicit transactions); keep them short; no external calls inside.
6. **Bulk operations bypass the per-row path:** `createMany`, `bulk_create`, `ExecuteUpdate`/`ExecuteDelete`, set-based `update where` - a thousand `save()` calls in a loop is a thousand round trips (and know what the bulk path skips: hooks, events, updated-at).
7. **Raw SQL is a legitimate escape hatch - used safely:** parameterized always (the ORM's raw APIs support binding - use it), typed result mapping, and a comment saying why the ORM couldn't express it.
8. **Concurrency: read-modify-write through entity objects races.** Atomic column expressions (`increment`, `F()`, `sql`\`x + 1\`), optimistic concurrency (version columns - EF concurrency tokens, `xmin`), or row locks - pick one per hot path.

## Tool-specific sharp edges

9. **Prisma:** the schema file is the source of truth - migrate via `prisma migrate dev/deploy`; one PrismaClient instance per process (hot-reload dev needs the global-singleton pattern); `$transaction` for atomicity (interactive transactions kept short); beware implicit `include` explosions on deep relations.
10. **Drizzle:** it's SQL-first - lean into that: schema in TS as truth, `drizzle-kit` for migrations, prefer query-builder joins/`with` over lazy patterns (there is no lazy loading - an advantage; don't reinvent it in loops).
11. **SQLAlchemy:** session lifecycle is everything - one session per request/unit-of-work, no session sharing across threads/tasks, know 2.0 style (`select()` + `session.execute`) vs legacy `Query`; `expire_on_commit` and detached-instance errors are lifecycle smells, not annotations to suppress. Async sessions never mix with sync engine calls.
12. **Entity Framework Core:** `AsNoTracking` for reads (tracking is the silent memory/CPU tax), DbContext is scoped and never shared across threads, `SaveChanges` batches - don't call it per entity, split queries (`AsSplitQuery`) for multi-`Include` cartesian explosions, and never lazy-loading proxies without a stated reason.
13. **Any ORM in a serverless environment:** connection pooling is the crisis point - use the platform's pooler (RDS Proxy, PgBouncer, Prisma Accelerate-class tooling) or connection limits per instance; a thousand lambdas each opening five connections is a database outage.
