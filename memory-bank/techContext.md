# Tech Context

## Runtime
- Node >=22.13.0, pnpm 9.15.0, turbo ^2.3.0, TypeScript 5.9.3 (strict).
- NestJS 11, Prisma 6, PostgreSQL 16 (Neon, RLS), Redis 7 (Upstash).

## Commands (repo root)
- `pnpm lint` · `pnpm typecheck` · `pnpm test` · `pnpm build`
- Scoped: `pnpm --filter @rihal/api lint|typecheck|test`; `pnpm --filter @rihal/database typecheck|test`
- DB: `pnpm db:generate` then `pnpm db:migrate`; `pnpm db:seed`; `pnpm db:studio`
- After schema edits: `npx prisma format` and `npx prisma validate`.

## Local environment
- Env files: `.env` (root). Never read/print secrets.
- `DATABASE_URL` uses app role `rihal_app`; `DIRECT_URL` uses migrator role `rihal_migrator`.
- API: port 4000 (default), global prefix `/api`, CORS origin `http://localhost:3000`.
- No Docker/PostgreSQL guaranteed locally; Prisma engine download may fail offline. CI runs full PostgreSQL verification.

## Roles
- `rihal_app`: non-owner, no SUPERUSER/BYPASSRLS/CREATEROLE/CREATEDB; SELECT/INSERT/UPDATE only; no real DELETE (archiving).
- `rihal_migrator`: owns schema/tables; migrations + seed only. Never shared with app.

## Auth
- `AUTH_SECRET` >=32 chars mandatory. Production requires HTTPS `AUTH_URL`, `SMTP_URL`, `SMTP_FROM` (STARTTLS/SMTPS).