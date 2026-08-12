---
title: Code craft - specificity and completeness
tags: [naming, completeness, stubs, specificity, abstraction, magic-numbers]
modes: [core, code, review]
order: 20
---

# Code craft - specificity and completeness

Guidance for writing code that reads as deliberate and human-authored. Pair with the
language rules in `rules/`.

## Name things exactly

Vagueness is the tell of generated code. Be specific by default:

- **Libraries by name**, not category - `httpx`, `asyncio`, `pydantic`, not "a
  networking library."
- **Protocols/APIs by name** - `TCP SYN`, `TLS 1.3`, `GET /api/v2/metrics`, not "the
  connection" or "the endpoint."
- **Patterns named, not described** - `producer-consumer`, `backpressure`,
  `asyncio.Queue`, not "a queue-based approach."
- **Exact error types** - `ConnectionRefusedError`, `TimeoutError`, `struct.error`,
  not "if something goes wrong."
- **Real numbers** - a `2.5`s timeout, a `65535`-byte buffer, port `443` - not
  `SOME_TIMEOUT` / `BUFFER` / `PORT` placeholders left for later.
- **Specific versions** - "Python 3.11", "kernel 5.15+", not "Python 3" / "recent
  Linux." Verify the installed version before relying on version-specific behavior.
- **Named architecture** - "the listener thread", "the flush interval", not "the main
  part."

When you pick an approach, name the alternative you rejected and why - one sentence,
in a comment or the reply. It shows the choice was deliberate.

> Only assert an identifier (library, flag, signature, version) you have actually
> seen or verified this session. A specific-but-invented name is worse than an honest
> "check the installed version." (See `guides/AI-PITFALLS.md` on confabulation.)

## Deliver complete code

- No `# TODO`, no stubs, no `pass` bodies, no "you can extend this later."
- Real imports, real error handling - never `except Exception: pass`.
- Precise names: variables for what they *hold* (`packet_queue`, `payload_bytes`),
  functions for what they *do* (`drain_queue`, `compute_checksum`) - not `data`,
  `value`, `process`, `handle`.
- No magic numbers without context: `65535` alone is fine; annotate it
  (`# max UDP payload`) or hoist to a named constant when it's used more than once or
  its meaning isn't obvious.
- Right-size abstraction: if three lines do the job, write three lines - not a class,
  factory, or pattern the problem didn't ask for.
- Match the surrounding codebase's style, naming, and test framework rather than
  importing a new one. Foreign-but-correct code is still a defect.

## Self-check

- [ ] Every identifier here is one I've seen/verified, or flagged as to-verify.
- [ ] No stubs, TODOs, or placeholder constants with no value.
- [ ] Error handling is real; no bare/empty excepts.
- [ ] Names say what things hold/do; abstraction matches the problem size.
- [ ] Style and test framework match the existing codebase.
