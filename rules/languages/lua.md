# Lua

1. **`local` everything.** Globals are the default and the disease - an undeclared assignment creates a global silently, and a typo'd read returns `nil` instead of erroring. Declare `local` at first use; lint with luacheck.
2. **Know your target runtime:** Lua 5.1 (and LuaJIT), 5.2, 5.3, 5.4 differ meaningfully (integer division, `goto`, bitwise ops, `#` semantics, `setfenv` vs `_ENV`). Embedded hosts (Neovim, Roblox, game engines, Redis) each pin one - check before writing.
3. **1-based indexing and `#` truthiness:** arrays start at 1; `#t` is unreliable on tables with nil holes - never `t[#t+1]` into a table that may contain nils; use an explicit count or `table.insert`.
4. **Only `nil` and `false` are falsy** - `0` and `""` are truthy. The `x = a and b or c` ternary idiom breaks when `b` is `false`/`nil`.
5. **Tables are the only data structure - be deliberate:** array part vs hash part, `ipairs` for sequences (stops at first nil), `pairs` for maps (no order guarantee). Don't mix array and map usage in one table casually.
6. **Errors:** `error()` with a message (or table) for failures; `pcall`/`xpcall` at boundaries that must survive; return `nil, err` for expected failures per Lua convention - and check both returns at call sites.
7. **OOP via metatables follows the project's existing pattern** (plain `setmetatable` classes, middleclass, host-provided class systems). Don't introduce a second object model.
8. **Scope closures carefully in loops** - each iteration gets a fresh local in Lua (unlike old JS), but upvalue-capturing hot-path closures allocate; hoist in performance-critical code (especially LuaJIT).
9. **String building:** `table.concat` for loops, not `..` accumulation (quadratic). Remember strings are interned and immutable.
10. **Performance in hot paths (game scripting):** localize repeatedly-used globals (`local floor = math.floor`), avoid creating tables per frame, know that `pairs` is slower than numeric loops under LuaJIT.
