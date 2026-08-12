# Go

## Errors - the heart of Go review

1. **Every error is handled at the call site: checked, wrapped-and-returned, or (rarely) explicitly discarded with a stated reason.** `_ =` on an error is a decision that needs a comment.
2. **Wrap with context on the way up:** `fmt.Errorf("loading config %s: %w", path, err)`. `%w` preserves the chain for `errors.Is`/`errors.As`; use those instead of string-matching error text.
3. **Sentinel errors (`errors.New`) as package-level `ErrX` variables; custom types when callers need data.** Return errors, don't panic - `panic` is for programmer errors (impossible states), and libraries never panic across their API.
4. **Don't log and return the same error** - that produces duplicate noise. Handle it once, at the level that decides what to do.

## Idiomatic shape

5. **`gofmt`/`goimports` output is not negotiable.** Also run `go vet`; respect the project's linter config (`golangci-lint`).
6. **Accept interfaces, return structs.** Define interfaces where they're *consumed*, keep them small (1-3 methods). A package exporting an interface plus its only implementation is Java smuggled into Go.
7. **Zero values should be useful** (`var buf bytes.Buffer` works). Design types so the zero value is valid, or provide a `NewX` constructor and document that it's required.
8. **Early returns, shallow nesting, no `else` after a returning `if`.** Happy path at minimal indentation.
9. **Short names in short scopes (`i`, `r`, `buf`), descriptive names at package level.** No stutter: `user.New`, not `user.NewUser`.

## Concurrency

10. **Every goroutine needs a known exit path before you start it.** Who stops it, and when? A goroutine blocked forever on a channel nobody closes is a leak.
11. **`context.Context` is the first parameter of anything that blocks, does I/O, or spawns work** - and it's honored (`select` on `ctx.Done()`, pass it to downstream calls). Never store a context in a struct.
12. **Channels: the owner (writer side) closes; receivers never close.** Prefer `sync.WaitGroup`/`errgroup.Group` for fan-out with error collection.
13. **Guard shared state with a mutex or don't share it.** Run tests with `-race` - a race detector hit is a bug, full stop, even if output "looks fine."
14. **Know the loop-variable capture rules for your Go version** (pre-1.22 loop vars are shared across iterations - shadow them; 1.22+ fixed it). Check `go.mod` for the version.

## Structure

15. **Small number of focused packages; no `utils`/`common` dumping grounds.** Package name is part of every call site's readability.
16. **Table-driven tests with subtests (`t.Run`)** are the house style. Test through exported APIs (`package foo_test`) unless internals genuinely need it.
17. **`defer` for cleanup immediately after acquiring the resource;** know that deferred calls in a loop pile up until function exit - extract a function if the loop is long.
