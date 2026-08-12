# Docker

## Images

1. **Multi-stage builds are the default:** build stage with toolchain -> minimal runtime stage (slim/alpine/distroless per ecosystem) copying only artifacts. Shipping compilers, dev dependencies, and source history in production images is size, attack surface, and secrets risk at once.
2. **Pin base images specifically** (`node:22-slim`, not `node:latest` - and digest-pin where supply-chain rigor demands); rebuild regularly for security patches; one obvious upgrade path.
3. **Layer order is cache strategy:** dependency manifests first (`COPY package.json pnpm-lock.yaml ./` -> install -> then `COPY . .`) so code changes don't bust the dependency layer. Combine related `RUN` steps; clean package-manager caches in the same layer that created them (a later `rm` doesn't shrink earlier layers).
4. **`.dockerignore` is mandatory:** `.git`, `node_modules`, env files, build outputs, secrets - a fat context is slow builds; a leaked `.env` in an image layer is a breach.
5. **Secrets never enter images:** no `ENV`/`ARG` secrets (ARGs persist in history), no COPYed key files - BuildKit `--mount=type=secret` for build-time needs, runtime injection (env/secret manager) for everything else. Scan images (trivy/grype) in CI.

## Runtime correctness

6. **Run as non-root:** create and `USER` an unprivileged user in the Dockerfile; read-only root filesystem where the app allows. Container-breakout defense starts here.
7. **PID 1 must handle signals:** exec-form `CMD ["app", "--flag"]` (shell form wraps in `sh -c` and eats SIGTERM); `--init`/tini for processes that don't reap or forward - otherwise graceful shutdown is a lie and orchestrators SIGKILL after the grace period.
8. **One process/concern per container;** logs to stdout/stderr (the platform collects them - no log files inside containers); writable data on volumes, never in the container layer.
9. **`HEALTHCHECK` (or orchestrator probes) reflecting real readiness** - an HTTP 200 from a process that can't reach its database is a lying health check.

## Compose and workflow

10. **Compose files declare the dev environment honestly:** service dependencies with `depends_on` + healthcheck conditions (started != ready), named volumes for data, env via `env_file` (gitignored) with a committed `.env.example`, ports bound to localhost in dev.
11. **Dev/prod parity with explicit divergence:** same base image and version pins; differences (bind mounts, debug flags, hot reload) isolated in an override file - not a separate hand-drifted Dockerfile.
12. **Resource limits declared** (compose `deploy.resources` / runtime flags) - an unbounded container OOMs the host, not just itself; and know your platform's architecture (`--platform`/multi-arch buildx) before shipping images built on ARM Macs to x86 servers.
