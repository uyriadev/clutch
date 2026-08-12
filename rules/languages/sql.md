# SQL

## Safety first

1. **Parameterized queries, always.** No string interpolation of values into SQL, ever, in any language binding. Dynamic identifiers (table/column names) come from allowlists.
2. **Writes without a `WHERE` clause are presumed bugs.** Before running any `UPDATE`/`DELETE`, run the same predicate as a `SELECT COUNT(*)` and sanity-check the number. In interactive sessions, wrap destructive statements in an explicit transaction so you can roll back.
3. **Migrations are forward-only scripts under version control** with a tested rollback path. Never hand-edit schema on a live database outside the migration flow.

## Correctness traps

4. **NULL breaks intuition:** `NULL = NULL` is not true, `NOT IN (subquery-with-null)` returns nothing, aggregates skip NULLs. Use `IS [NOT] NULL`, `IS DISTINCT FROM`, `NOT EXISTS` (instead of `NOT IN`), and `COALESCE` deliberately.
5. **`COUNT(*)` counts rows; `COUNT(col)` counts non-null values.** Know which you mean.
6. **Every `GROUP BY` output column is either grouped or aggregated.** Databases that let you break this rule (old MySQL) return nondeterministic garbage.
7. **`ORDER BY` or it's unordered.** Result order without an explicit `ORDER BY` is an implementation accident that will change under you. Pagination requires a deterministic total order (add a unique tiebreaker column).
8. **JOIN direction matters with filters:** a `WHERE` condition on the right table of a `LEFT JOIN` silently converts it to an inner join - put the condition in the `ON` clause if you meant to keep unmatched rows.

## Schema and query design

9. **Explicit column lists** - `SELECT *` in application code breaks when the schema evolves and drags unneeded bytes; `INSERT` without a column list breaks on column reorder.
10. **Right types:** money as `DECIMAL`/integer minor units (never float), timestamps with time zone semantics understood (`timestamptz` in Postgres), text constraints where they encode invariants.
11. **Foreign keys, NOT NULL, UNIQUE, CHECK - declare the invariants.** Application-side enforcement alone lasts until the second writer shows up.
12. **Index what you filter, join, and sort on - and no more.** Every index taxes writes. Composite index column order follows the query (equality columns first, then range/sort). Confirm with `EXPLAIN`, don't guess.
13. **A leading wildcard (`LIKE '%x'`) or a function on the column (`WHERE lower(email) = ...`) defeats the index** - use full-text search or expression indexes respectively.

## Transactions

14. **A transaction spans exactly the statements that must be atomic - and nothing slow.** No network calls or user waits inside a transaction; long transactions hold locks and bloat.
15. **Know your isolation level and its anomalies.** Read-modify-write cycles need `SELECT ... FOR UPDATE`, an atomic single statement (`UPDATE ... SET x = x + 1`), or optimistic versioning - a plain read-then-write races.
16. **Batch multi-row work:** one `INSERT ... VALUES (...), (...), (...)` or a bulk-load path, not a statement per row in a loop.
