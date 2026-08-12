# R

1. **Pick the dialect the project uses and stay in it:** tidyverse (dplyr/tidyr pipelines), data.table, or base R. Mixing all three in one script is the most common readability failure in R code.
2. **Vectorize; don't loop over rows.** R's model is whole-vector operations (`x * 2`, `ifelse`/`dplyr::if_else`, `rowSums`). An explicit `for` over data-frame rows is almost always wrong; `apply` family or `purrr::map_*` when iteration is real.
3. **Never grow objects in a loop** (`x <- c(x, new)` is quadratic). Preallocate (`vector("list", n)`) or build with `lapply`/`map` and combine once.
4. **`<-` for assignment** (per style), `=` only for function arguments. Style per the tidyverse style guide; lint with `lintr`, format with `styler` if the project does.
5. **NA is not NULL is not NaN:** `NA == NA` is `NA` - test with `is.na()`; comparisons and aggregates propagate NA unless `na.rm = TRUE` (state the choice deliberately). `NULL` removes list elements; `NA` holds a place.
6. **Type gotchas:** `stringsAsFactors` (pre-R4.0 legacy), factors silently converting to integer codes (`as.numeric(as.character(f))` for the values), `1:0` counting down when a length is zero - use `seq_len(n)`/`seq_along(x)` in loops, never `1:length(x)`.
7. **`dplyr::if_else`/`case_when` over nested `ifelse`** (type-stable, NA-explicit). In functions using tidy evaluation, embrace `{{ }}`/`.data[[col]]` - don't paste-and-parse expressions.
8. **Functions over copy-pasted script blocks;** explicit `return` optional but arguments validated at the top (`stopifnot`, `rlang::abort` with messages). Avoid `attach()` and mutating globals from functions (`<<-` needs justification).
9. **Reproducibility is a deliverable:** `set.seed()` before anything stochastic, `renv` for dependency pinning, scripts that run top-to-bottom in a fresh session (no reliance on leftover workspace; never save/restore `.RData` implicitly).
10. **Data I/O:** `readr`/`data.table::fread` over base `read.csv` for real data (speed, encoding, type inference control); explicit column types for anything production-shaped.
11. **Joins and pipelines beat repeated subscript surgery:** `left_join` with explicit `by =`, checked expectations on row counts after joins (many-to-many surprises are the classic silent data bug).
