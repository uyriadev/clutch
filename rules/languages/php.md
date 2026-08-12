# PHP

## Modern PHP or nothing

1. **Check the PHP version constraint (`composer.json`) first.** Modern PHP (8.x) has constructor promotion, enums, readonly properties, named arguments, first-class callables, `match` - use them at the project's floor, never above.
2. **`declare(strict_types=1);` at the top of every new file** (in codebases using it - most modern ones). Type declarations on all parameters, returns, and properties; nullable types (`?Foo`) explicit.
3. **`===`/`!==` always.** PHP's `==` type juggling (`0 == "a"` history, `"1e3" == "1000"`) is a bug generator. Same for `in_array`/`array_search`: pass `strict: true`.

## Structure

4. **PSR-12 formatting, PSR-4 autoloading, Composer for everything.** No `require`/`include` chains for classes; no functions in global namespace in application code.
5. **Constructor injection over statics and globals.** `global $db` and static service locators make code untestable; match the framework's container.
6. **Enums (8.1+) over class constants for closed sets;** readonly value objects over associative arrays for structured data passed between layers - `$user['emial']` is a runtime typo, `$user->email` isn't.
7. **`match` over `switch`** where each arm yields a value - it's strict-comparing and exhaustive (throws on unhandled).

## The classic traps

8. **Arrays are PHP's everything-type - contain the blast radius:** document shapes (`@param array{id: int, name: string}` or better, use objects), don't mutate arrays passed by reference without clear need (`&` parameters are surprise machines).
9. **Error handling:** exceptions over error codes; never `@`-suppress errors; convert warnings to exceptions in dev. Catch specific exception types; `\Throwable` only at top-level handlers.
10. **String/number coercion:** validate and cast explicitly at boundaries (`filter_var` for emails/ints, dedicated validators in frameworks). `$_GET`/`$_POST` values are always strings and always hostile.
11. **`null` propagation:** nullsafe operator `?->` over nested isset-checks; `??` for defaults (knows the difference from `?:`, which also swallows `''`/`0`/`false`).

## Security (PHP-specific emphasis)

12. **PDO/prepared statements only** - no string-built SQL, no `mysqli_query` with interpolation.
13. **Output escaping per context:** `htmlspecialchars` (with `ENT_QUOTES`) for HTML, or the template engine's auto-escaping (Twig/Blade) - never `echo $userInput`.
14. **`password_hash`/`password_verify` for passwords;** `random_bytes` for tokens. Never `md5`/`sha1` for anything security-relevant.
15. **Never `unserialize` untrusted data** (object injection); use JSON. Never pass user input to `include`, `eval`, `system`, or file functions without allowlisting.
