# Prisma 6 & Multi-Tenant Rules

## Tenant Isolation (MANDATORY)
- EVERY query on tenant-scoped tables MUST include `where: { tenantId: currentTenantId }`.
- Never write a `findMany`/`findFirst`/`update`/`delete` without a tenant filter unless it is an explicit admin/system task.
- Access tenant-scoped tables only through `PrismaService` / `withTenant`. No cross-tenant data leakage.
- After writing Prisma queries, review them to ensure strict tenant isolation.

## Schema
- Keep schema modular. Run `npx prisma format` and `npx prisma validate` after any changes.
- Schema/migrations only via Prisma; never edit existing migration SQL.

## Migrations
- Generate migrations using `npx prisma migrate dev --name <descriptive_name>`. Never edit migration files manually.
- For DB changes: `pnpm db:generate` then `pnpm db:migrate`.
- Never run destructive DB commands (`migrate reset`, `db push --force-reset`) without explicit user approval.