# Scala

1. **Know the Scala version and the house dialect first.** Scala 2.13 vs 3 differ syntactically (given/using, enums, indentation syntax, `implicit`); and codebases range from "Java with vals" to full Cats/ZIO functional. Match what's there - don't import a paradigm.
2. **Immutability by default:** `val` over `var`, immutable collections (the default `scala.collection.immutable`), case classes for data with `copy` for updates.
3. **Model with ADTs:** sealed traits (Scala 2) / enums (Scala 3) + case classes, matched exhaustively - the compiler warns on missing cases only if the hierarchy is sealed, so seal it. No wildcard match arms on your own ADTs.
4. **`Option`/`Either`/`Try` over null and thrown exceptions in pure code.** Never `.get` on an Option/Try (use `fold`, `getOrElse`, pattern matching); `Either` with a meaningful error type for expected failures. Nulls exist only at the Java boundary - wrap immediately (`Option(javaCall())`).
5. **for-comprehensions for sequencing monadic steps** (Option/Either/Future/IO) over nested `flatMap` ladders - but keep them short; a 15-line for-comprehension needs decomposition.
6. **Futures need an execution context and error handling:** don't `import global` reflexively in library code, don't `Await` outside main/tests, `recover`/`transform` for failure paths. In Cats Effect/ZIO codebases, use the effect type - don't mix raw Futures in.
7. **Implicits/givens are for well-known type classes and context, not spooky action:** every implicit conversion needs strong justification (Scala 3 makes you opt in - respect that). Keep implicit scope discoverable (companion objects).
8. **Pattern matching over isInstanceOf/casting, always.** Destructure in `match`, in `val` bindings, and in partial functions - safely (`case x: Foo =>`, not `.asInstanceOf`).
9. **Collections: know the cost.** `List` is a linked list (prepend cheap, index/append linear); `Vector` for general indexed use; `view`/iterator for large chained transforms. Avoid `Seq#contains` in loops - use a `Set`.
10. **Keep it boring:** methods with type signatures a colleague can read, no operator-name APIs (`|+|` aside for known type classes), no symbolic soup, minimal type-level cleverness unless the project is already there.
11. **sbt hygiene:** cross-version compatibility respected, warnings-as-errors honored (`-Xfatal-warnings` codebases: fix, don't suppress), scalafmt config obeyed.
