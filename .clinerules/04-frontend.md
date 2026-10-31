# Frontend (Next.js 15) — Planned, not yet implemented

> Status: frontend not yet present in repo. Apply these rules when `apps/web` (or similar) is added.

## Structure
- Next.js 15 App Router. Server Components by default; mark Client Components explicitly (`'use client'`).
- TypeScript strict mode. No `any` without justification.

## Data fetching
- Server Components fetch via server-side calls to the API; never expose secrets to the client.
- Client-side mutations go through typed API client; handle loading/error states.

## Multi-tenancy (Frontend)
- Never send `tenantId` from client; rely on authenticated session/JWT.
- Tenant context comes from auth session only.

## State & styling
- Prefer server state; use minimal client state. Tailwind + shadcn/ui if adopted (confirm before use).
- Keep components small and composable; colocate tests.

## Testing
- Add component/e2e tests when frontend exists; verify via Playwright MCP.