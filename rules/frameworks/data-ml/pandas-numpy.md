# pandas & NumPy

## The cardinal rule

1. **Vectorize; never loop over rows.** `df.iterrows()` in production code is a defect: use column arithmetic, `np.where`/`np.select` for conditionals, `.map` for dict lookups, `merge` for enrichment, groupby for aggregation. `.apply(axis=1)` is a loop in a costume - last resort, stated as such.

## Correctness traps that produce silent wrong answers

2. **`SettingWithCopyWarning` is never ignored:** chained indexing (`df[df.x > 0]['y'] = 1`) may modify a copy. Use `.loc[mask, 'y'] = 1`; take explicit `.copy()` when you mean a copy. (pandas 3.0's copy-on-write makes chained assignment simply not work - write it correctly regardless.)
3. **Merges get audited:** wrong join keys and unexpected many-to-many joins silently duplicate rows. Assert expectations - `validate='one_to_one'`/`'many_to_one'` on merges, row-count checks after, `indicator=True` when diagnosing.
4. **NaN semantics:** NaN != NaN (use `isna()`), NaN poisons sums/means per pandas defaults differently than NumPy (`skipna` vs propagate - know which you're getting), int columns with NaN silently become float (nullable dtypes `Int64` where it matters), and comparisons with NaN are False - inverted masks (`~mask`) can therefore surprise.
5. **Dtypes are checked, not assumed:** `object` columns of mixed junk break operations late - coerce early (`astype`, `to_numeric(errors=...)` deliberately, `to_datetime` with explicit `format`), categoricals for low-cardinality strings, and never compare across dtypes and trust the result.
6. **Timezone-aware or bust for real timestamps:** localize/convert explicitly (`tz_localize`/`tz_convert`); naive-vs-aware comparisons raise, and implicit local time corrupts data across DST.
7. **`inplace=True` is deprecated practice** - assign the result. Method chains (`.assign`, `.pipe`, `.query` where readable) keep transformations auditable.

## NumPy specifics

8. **Broadcasting is checked mentally before trusted:** shape mismatches that *don't* error are the dangerous ones ((n,1) vs (n,) creating (n,n)). Assert shapes at function boundaries in numeric code.
9. **Views vs copies:** basic slicing views (mutations propagate!), fancy indexing copies. When it matters, be explicit (`.copy()`); check `flags` when debugging aliasing.
10. **Float discipline:** `np.isclose`/`allclose` for comparisons, accumulation error awareness in long sums (`math.fsum`/Kahan where it matters), integer overflow in fixed-width dtypes wraps silently - size dtypes to the data.
11. **`np.random.default_rng(seed)` (Generator API), seeded, passed explicitly** - module-level `np.random.*` calls make results irreproducible and tests flaky.

## Scale and pipelines

12. **Memory is finite:** load only needed columns (`usecols`, parquet column selection), chunk large reads, prefer parquet over CSV for intermediates (types survive), `category`/downcasting for wide data. If it doesn't fit, the answer is polars/duckdb/dask per project - not swap.
13. **Pipelines are functions with contracts:** input/output schema stated (or validated with pandera-style checks where adopted), no cell-order-dependent notebook state in production paths, seeds and versions pinned for anything that feeds a model.
