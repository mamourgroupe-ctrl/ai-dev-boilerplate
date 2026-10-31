# Rihal — Project Brief

- Multi-tenant SaaS platform for Hajj/Umrah agency operations (pilgrims, groups, documents, invoices, notifications, agency subscriptions).
- Monorepo: Turborepo + pnpm workspaces (`apps/*`, `packages/*`).
- `apps/api` — NestJS 11 backend (`@rihal/api`); `packages/database` — Prisma 6 schema/migrations/seed (`@rihal/database`).
- Frontend (Next.js 15) planned, not yet present.
- Stack: TypeScript 5.9 strict, NestJS 11, Prisma 6, PostgreSQL 16 (Neon, RLS), Redis 7 (Upstash), Auth.js v5.
- Tenant isolation is the top priority: RLS + AsyncLocalStorage TenantContext + `PrismaService.withTenant`.
- Current branch: `feat/agencies-controller` (agencies subscription endpoints). Phase 4 (RLS) PR #13 open pending human security review; phases 5-7 deferred.