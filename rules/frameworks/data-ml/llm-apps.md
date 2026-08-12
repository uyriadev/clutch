# LLM Applications - SDKs, RAG, Agents

Covers Anthropic/OpenAI SDK usage, LangChain/LlamaIndex-style orchestration, and general LLM-app engineering.

## API usage fundamentals

1. **Model IDs, parameters, and pricing change faster than any training data - verify against current docs/the project's config, never from memory.** Centralize the model name in config; hardcoded model strings scattered through code age like milk.
2. **Every LLM call handles: rate limits (429 -> exponential backoff with jitter), timeouts, overloaded/5xx retries, and context-length errors.** Use the official SDK's built-in retry support where it exists; log request IDs for support escalation.
3. **Stream user-facing responses** - perceived latency is the product. Handle partial-output states and mid-stream errors (the connection can die after tokens arrived).
4. **Count and cap tokens deliberately:** know the model's context window, budget input vs output, truncate/summarize history with an explicit strategy (not silent tail-dropping that deletes the system prompt or the user's question).
5. **Costs are engineering:** cache-friendly prompt structure (stable prefix first - system prompt, tools, docs; variable content last) to exploit prompt caching; batch APIs for offline work; small-model routing for easy calls. Log per-request token usage from day one.

## Prompt engineering as code

6. **Prompts are versioned artifacts, not string literals:** stored in files/templates with placeholders, reviewed in diffs, changelogged - a prompt tweak is a deploy.
7. **Structure beats prose:** clear role/system instruction, delimited sections (XML tags work well), explicit output format with an example, instructions for the refusal/unknown case ("if the answer isn't in the context, say so") - the unhappy path must be specified or the model invents.
8. **Untrusted content is data, never instructions:** user input and retrieved documents go in clearly delimited data sections; assume prompt injection exists - anything the model reads can try to steer it. Never let retrieved/user text define tool calls or system behavior without validation downstream.

## Structured output and tools

9. **Schema-constrained output over parse-and-pray:** tool/function calling or JSON mode with a defined schema, validated on receipt (zod/pydantic) with a bounded retry-on-invalid loop. Regexing JSON out of markdown fences is a last resort, not a design.
10. **Tools are narrow, typed, and safe-by-construction:** descriptions written for the model (when to use, when not), parameters validated server-side like any API input, destructive operations gated on confirmation - the model *will* eventually call every tool you give it with every input you didn't expect.
11. **Agent loops get budgets:** max iterations, max cost, timeouts, and a terminal "give up and report" state - an unbounded tool-calling loop is an unbounded bill.

## RAG

12. **Retrieval quality is measured, not vibed:** evaluate retrieval separately from generation (does the right chunk surface for a set of known questions?) before blaming the model. Chunking strategy (size, overlap, structure-aware splits) is the highest-leverage knob.
13. **Ground and cite:** the prompt instructs answering from the provided context with source attribution; below a relevance threshold, say "not found" rather than letting the model freestyle. Embeddings: same model for index and query, versioned - mixed embedding versions silently break retrieval.

## Evaluation and safety

14. **No eval, no ship:** a test set of real prompts with graded expected behaviors, run on every prompt/model change - LLM-as-judge for scale (spot-audited by humans), regression-gated in CI where feasible. "It looked good on three examples" is not evaluation.
15. **Log everything (redacted):** prompts, completions, latency, tokens, model version - you cannot debug or improve what you didn't record; scrub PII per policy before storage.
16. **Non-determinism is a design constraint:** pin versions where reproducibility matters, design UX for variance, never build logic that assumes byte-identical outputs across calls.
