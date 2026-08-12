# Ruby

## Idiomatic core

1. **Follow the community style guide / RuboCop config in the repo** - two-space indent, `snake_case` methods, `CamelCase` classes, predicate methods end in `?`, dangerous variants in `!`. Run RuboCop; fix, don't disable (inline `rubocop:disable` needs a reason).
2. **Blocks and enumerables are the language:** `map`, `select`, `reject`, `each_with_object`, `group_by`, `sum` over manual loops and accumulator mutation. `find` not `select.first`; `any?` not `count > 0` (short-circuits).
3. **Guard clauses and early returns;** trailing conditionals (`return if x.nil?`) for one-liners only. Avoid `unless` with `else` or with compound conditions.
4. **Symbols for identifiers, strings for data.** Frozen string literals magic comment (`# frozen_string_literal: true`) where the project uses it.

## Nil and truthiness

5. **Only `nil` and `false` are falsy** - `0` and `""` are truthy (opposite of JS/Python instincts; don't write `if count` meaning nonzero).
6. **Safe navigation `&.` for genuinely-optional receivers,** not as a blanket reflex that hides nils which shouldn't exist. `fetch` over `[]` for hashes when absence is a bug (`params.fetch(:id)` fails loudly).
7. **Return early over deeply nil-checked chains;** consider the Null Object pattern where nil-handling spreads.

## Structure

8. **Small objects, single responsibility, composition via modules used sparingly** - a mixin is inheritance with worse tooling; prefer explicit collaborator objects for complex behavior.
9. **`attr_reader`/`attr_accessor` over hand-written accessors;** keep instance-variable access behind them even internally.
10. **Keyword arguments for methods with 2+ parameters of the same type or optional parameters** - `create_user(name:, admin: false)` reads at the call site.
11. **Exceptions:** raise specific classes (subclass `StandardError`), rescue specific classes - a bare `rescue` (or `rescue Exception`) catches signals and `SystemExit`, which is almost never intended. Don't use exceptions for expected control flow.
12. **Metaprogramming (`method_missing`, `define_method`, monkey-patching) is a loaded weapon:** last resort, tightly scoped, with `respond_to_missing?` implemented. Never monkey-patch core classes in application code (Rails already did enough of that).

## Environment

13. **Bundler always:** `bundle exec` context, `Gemfile.lock` committed, Ruby version pinned (`.ruby-version`). Match the project's Ruby version before using new syntax (pattern matching `case/in` 2.7+, endless methods 3.0+, `Data.define` 3.2+).
14. **Mutable default trap exists here too:** constants holding mutable objects should be frozen (`VALID = %w[a b].freeze`).
