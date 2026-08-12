# Astro

1. **Zero JavaScript is the default and the point.** `.astro` components render to HTML at build/request time; ship a framework island only where interactivity genuinely exists. If a component just displays data, it has no business being a React/Vue island.
2. **Choose `client:` directives deliberately:** `client:visible` for below-fold widgets, `client:idle` for non-urgent, `client:load` only for immediately-needed interactivity, `client:only` when SSR of the island is impossible. Every directive is a bundle-size decision.
3. **Islands are isolated:** no shared framework context across islands (each hydrates independently). Share state via nano stores (or plain module state + custom events), pass data down as serializable props - a React context provider cannot wrap a sibling island.
4. **Fetch in frontmatter:** the code fence at the top of `.astro` files runs server-side - `await` freely there, use `Astro.props`, `Astro.params`. Secrets are safe in frontmatter and endpoints, never in island props (props are serialized into the HTML).
5. **Know the rendering mode per page:** static (default), or server-rendered via adapter with `export const prerender = false` (or project-wide `output: 'server'`). Server-only features (`Astro.request` headers, cookies) silently misbehave on prerendered pages - check the mode before using them.
6. **Content collections for structured content:** define schemas (`src/content.config.ts`, zod) so frontmatter is typed and validated at build; query with `getCollection`. Don't glob markdown files by hand.
7. **Use the built-ins before dependencies:** `<Image />`/`getImage` for optimized images, view transitions API integration, `getStaticPaths` for dynamic static routes (with typed params), redirects in config, `astro:env` for typed env vars.
8. **Endpoints (`src/pages/api/*.ts`) for APIs and form handling:** standard Request/Response, validate input, check auth per endpoint - same server-endpoint discipline as any backend. Astro Actions (4.15+) for typed client-server calls where adopted.
9. **Scoped styles by default:** `<style>` in `.astro` scopes to the component; `is:global` deliberately and rarely. Tailwind via the official integration if the project uses it.
10. **Middleware (`src/middleware.ts`) for auth/headers/locals** - typed `Astro.locals` via `env.d.ts`; keep it thin, it runs on every request in server mode.
11. **Version check:** Astro 4->5 moved content config and changed collections API (`type: 'content'` -> loaders); adapter APIs shift between majors. Verify against the installed version.
