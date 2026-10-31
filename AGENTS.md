<!-- BEGIN:turborepo-agent-rules -->

# This is NOT the Turborepo you know

Turborepo configuration, task behavior, and CLI commands can vary between installed versions and may differ from your training data. Resolve the `turbo` package from this file's directory or relevant workspace; in monorepos, it may not be visible from the repository root. For example, run `node -p "require.resolve('turbo/package.json')"` from a workspace that depends on `turbo`.

Read `docs/README.md` inside that installed package first, then read the relevant pages from its `docs/` directory before changing Turborepo configuration or commands. Heed deprecation notices. These bundled docs match the installed package version and are available without network access.

This block is written and re-added by `turbo` before repository-scoped commands when an AI agent is detected. In the Turborepo source repository, its template is defined in `crates/turborepo-cli/src/cli/agent_guidance.rs`. Removing the managed block while updates are enabled means a later qualifying invocation will add it again. Set `"agentGuidance": false` in the root `turbo.json` or `turbo.jsonc` to opt out; this does not remove an existing block. Keep the block committed with your work to avoid an uncommitted change on the next agent invocation.
<!-- END:turborepo-agent-rules -->

# Rihal — Agent Instructions

## Project
Multi-tenant SaaS for Hajj/Umrah ops. Monorepo: Turborepo + pnpm (`apps/*`, `packages/*`).
- `apps/api` NestJS 11 (`@rihal/api`); `packages/database` Prisma 6 + PG 16 (`@rihal/database`); Frontend Next.js 15 planned.
Stack: TS 5.9 strict, NestJS 11, Prisma 6, PG 16 (RLS), Redis 7, Auth.js v5.

## Layout
`apps/api/src` (NestJS), `apps/api/test` (Vitest), `packages/database/prisma` (schema/migrations/seed), `docs/` (decisions, progress, data-retention, agent-state).

## Standards
- TS strict; no `any` w/o justification. Controllers thin; logic in services. Prisma via `PrismaService`/`withTenant`.
- Multi-tenant: `tenantId` from signed JWT only; never body/params. `path.join`/`path.resolve`.

## Security (HARD)
- Never read/print/copy `.env*`, `*.pem`, `*.key`, `id_*`. No editing existing migration SQL.
- No destructive DB/shell cmds (`migrate reset`, `db push --force-reset`, `rm -rf`, force push) w/o approval. No secrets/agent dirs committed.

## Verify
`pnpm lint`·`typecheck`·`test`·`build` (or scoped `--filter`). DB: `pnpm db:generate` then `pnpm db:migrate`.

## Git/MCP
No `git add/commit/push` unless asked. Keep turbo block. Prefer `context7` MCP; `playwright` for UI. Windows: `cmd /c npx ...`.
