# Next.js (App Router)

## The server/client boundary - get this right first

1. **Server Components by default; `'use client'` only where interactivity lives** (event handlers, state, browser APIs, effect-dependent libraries). Push the directive to the leaves - marking a layout `'use client'` drags its whole subtree client-side.
2. **The boundary is one-way:** Server Components can render Client Components; Client Components can't import Server Components (pass them as `children`/props instead). Props crossing the boundary must be serializable - no functions, class instances, or Dates-you-expect-to-stay-Dates.
3. **Secrets stay on the server.** Only `NEXT_PUBLIC_*` env vars reach the browser - and anything so named *will* be shipped to every visitor, so audit each one. Server-only modules: `import 'server-only'` to make accidental client import a build error.
4. **Data fetching happens on the server** (async Server Components) as close to where it's used as possible - React dedupes identical fetches per render. Client-side fetching is for user-interactive/live data, via a query library.

## Routing and data conventions

5. **Use the file conventions for what they're for:** `loading.tsx` (streaming fallback), `error.tsx` (must be a client component), `not-found.tsx`, `layout.tsx` (persists across navigation - no per-page data), route groups `(name)` for organization. Don't reinvent these in-page.
6. **Server Actions for mutations** (`'use server'`) - and treat every action as a public endpoint: validate input (zod), check auth *inside the action*, then `revalidatePath`/`revalidateTag` for cache coherence. An unauthorized action is an unauthorized API.
7. **Know your caching layers and be explicit:** fetch cache, route cache, router cache change behavior across Next versions (15 flipped defaults to uncached). State the intent - `cache: 'no-store'`/`revalidate`/`dynamic = 'force-dynamic'` - instead of relying on remembered defaults; verify against the installed version.
8. **`next/navigation` in the App Router** (`useRouter`, `usePathname`, `useSearchParams`) - the `next/router` APIs are Pages Router only. `redirect()`/`notFound()` throw; don't wrap them in try/catch that swallows them.

## Performance conventions that are the point of Next

9. **`next/image` for images** (sizing, formats, lazy loading), **`next/font` for fonts** (self-hosted, zero layout shift), **`next/link` for navigation** (prefetching) - plain `<img>`/`<a>`/CSS `@import` fonts forfeit the framework's wins.
10. **`generateMetadata`/`metadata` export for SEO,** not hand-rolled `<head>` tags. `generateStaticParams` for known dynamic routes to pre-render.
11. **Suspense boundaries around slow data** so the shell streams - one slow await at the top of a page blocks everything below it.
12. **Route handlers (`route.ts`) for real APIs only** (webhooks, external consumers) - internal data flow goes through Server Components/Actions, not fetch-to-your-own-API round trips.

## Project hygiene

13. **Check the Next.js major version before writing anything** - App vs Pages Router, caching defaults, async `params`/`searchParams`/`cookies()` (15+), Turbopack flags all shifted. The installed version wins over memory.
14. **Middleware is edge-constrained:** keep it thin (auth redirects, rewrites, headers) - no Node APIs, no heavy work; it runs on every matched request.
