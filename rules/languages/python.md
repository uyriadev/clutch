# Python

## Idiomatic baseline

1. **Type hints on all function signatures** in any codebase that uses them at all. Modern syntax: `list[int]`, `str | None` (3.10+), not `List`/`Optional` unless the project targets older versions. Run the project's checker (mypy/pyright) if configured.
2. **f-strings for formatting.** `%` and `.format()` only where a template is stored before values exist. Exception: logging uses lazy `%` style (`logger.info("user %s", uid)`) so formatting is skipped when the level is off.
3. **Comprehensions for simple transforms; loops for anything with branching or side effects.** A comprehension you must read twice should be a loop.
4. **Iterate directly:** `for item in items`, `enumerate()` for indexes, `zip()` for parallel sequences. `range(len(x))` is a smell.
5. **EAFP over LBYL where natural:** `try/except KeyError` or `dict.get` over check-then-access, especially under concurrency where check-then-act races.

## The classic traps

6. **Never use mutable default arguments** (`def f(items=[])`). Default is evaluated once at definition. Use `None` and create inside.
7. **`is` for `None`/singletons only; `==` for values.** Small-int/string interning makes `is` comparisons deceptively pass in tests.
8. **Late-binding closures in loops:** `lambda: i` captures the variable, not the value. Bind explicitly: `lambda i=i: i`.
9. **Bare `except:` is forbidden;** it swallows `KeyboardInterrupt` and `SystemExit`. Catch specific exceptions; `except Exception` is the widest acceptable net, and only with logging/re-raise.
10. **Don't shadow builtins or stdlib module names** (`list`, `type`, `json.py` as a filename - the last one breaks imports mysteriously).

## Structure

11. **Dataclasses (or Pydantic at validation boundaries) over dict-shaped data** passed between functions. `user["emial"]` fails at runtime; `user.emial` fails at type-check.
12. **Context managers for every resource:** files, locks, connections, temporary state. If you `open()` without `with`, justify it.
13. **`pathlib.Path` over `os.path` string surgery.**
14. **Exceptions carry context:** `raise ValueError(f"invalid tier {tier!r}")`, and use `raise ... from err` when translating exception types so the chain survives.
15. **No import-time side effects; guard scripts with `if __name__ == "__main__":`.**

## Environment

16. **Every project runs in a virtualenv with pinned dependencies** (lockfile via uv/poetry/pip-tools - whatever the project uses; never `pip install` into system Python).
17. **Check the Python version floor before using new syntax** (`match`, walrus, `tomllib`, generics syntax) - read `pyproject.toml`'s `requires-python`.
18. **Concurrency: asyncio for I/O-bound with async libraries, threads for I/O-bound with blocking libraries, processes for CPU-bound.** Don't mix blocking calls into async code - one `requests.get` inside a coroutine stalls the whole loop; use an async client or `asyncio.to_thread`.
