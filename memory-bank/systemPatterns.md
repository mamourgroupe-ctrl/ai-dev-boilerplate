# System Patterns

## Architecture (DDD)
- Modules / Controllers / Services. Controllers thin; business logic in services.
- Validation via `class-validator` + `class-transformer`; `ValidationPipe`.
- `AuthGuard` (JWT) at controller level where required.
- Paths via `path.join`/`path.resolve` (Windows/WSL safe).

## Multi-tenancy (MANDATORY)
- `tenantId` resolved from signed JWT claims only — never request body/params.
- `TenantContext` (AsyncLocalStorage) populated by `TenantContextInterceptor` from `request.auth.tenantId`.
- `PrismaService.withTenant`/`withRequestTenant` sets `set_config('app.current_tenant_id', ..., true)` per transaction; every tenant-scoped query MUST include `where: { tenantId }`.
- RLS `ENABLE` + `FORCE ROW LEVEL SECURITY` on every tenant-scoped table (users, pilgrims, groups, members, documents, invoices/items, notifications, sessions, refresh/reset tokens).
- Tenant-independent tables (e.g. `tenants`, `subscriptionPlan`) carry no `tenantId`.

## Auth & sessions
- Access JWT 15 min HS256 with fixed issuer/audience; refresh opaque, SHA-256 stored, rotated on use; reuse revokes session.
- Session/user/tenant/role re-validated per protected request (immediate revocation).
- Refresh in `HttpOnly; SameSite=Strict` cookie (auth path); access token in body with `Cache-Control: no-store`.
- bcryptjs cost 12; recovery tokens one-time hashed, 15 min expiry; reset link AES-256-GCM via HKDF from `AUTH_SECRET`, delivered via outbox; sessions revoked on password change.

## Domain conventions
- Archiving via `archivedAt` instead of delete; FKs `ON DELETE RESTRICT`.
- Documents use private `storageKey`, not public URLs.
- Group size enforced in service within locked transaction + DB trigger; single active leader via partial unique index.
- Invoices optionally link to pilgrim with customer-name snapshot (no Customer entity).
- Rate limiting via `@nestjs/throttler` (in-memory per process; shared store needed for multi-replica).

## Testing
- Vitest for API + database packages; PostgreSQL tests skip without DB. Verification loop: lint/typecheck/test/build.