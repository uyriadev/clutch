# Elixir

1. **Pattern match; don't inspect.** Function-head matching and guards over conditional pyramids: `def handle({:ok, val})` / `def handle({:error, reason})` beats an `if` on tuple tags. Destructure in heads, `case`, and `with`.
2. **The `{:ok, val} | {:error, reason}` contract is sacred:** return tagged tuples from fallible functions; bang variants (`fetch!`) raise and exist for "failure is a bug" call sites. Never return bare values from functions that can fail.
3. **`with` for happy-path pipelines of fallible steps,** with an `else` that handles (or lets fall through) each failure shape. Don't use `with` for a single match - that's a `case`.
4. **Data is immutable - pipelines are the idiom:** `|>` chains transforming data through small functions. Start pipes with a bare value, keep steps arity-consistent; a pipe with one step is just a function call.
5. **Processes are for runtime concerns, not code organization:** reach for a GenServer to hold state, serialize access, or supervise a resource - not to namespace functions. Most code should be plain modules and functions.
6. **Let it crash - with supervision:** don't defensively rescue everywhere; design supervisors to restart cleanly. `try/rescue` is rare and deliberate (boundaries with side effects, third-party calls). Handle expected failures with tagged tuples, not exceptions.
7. **GenServer discipline:** keep `handle_*` callbacks thin (delegate to pure functions), never block a GenServer on a long call (offload to `Task`), remember calls to self deadlock. Name processes only when there's truly one.
8. **Know your data structures:** keyword lists for options (ordered, dupes allowed), maps for data, structs (`defstruct` + `@enforce_keys`) for shaped domain data with pattern-matchable type. Atoms are never created from user input (atom table doesn't GC - `String.to_existing_atom`).
9. **Enum vs Stream:** `Enum` is eager - fine for small data; `Stream` for large/lazy/composed pipelines and anything reading from IO. Avoid multiple passes when one `reduce` does it.
10. **Typespecs and docs on public functions** (`@spec`, `@doc`, `@moduledoc`); run Dialyzer if the project does. `mix format` output unedited; Credo findings fixed.
11. **Tests: ExUnit with `async: true` wherever tests don't share global state** - design for it (no shared named processes, sandboxed Ecto). Doctests for pure functions keep docs honest.
