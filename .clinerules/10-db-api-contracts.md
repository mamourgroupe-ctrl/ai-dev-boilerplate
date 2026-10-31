---
paths: ["prisma/**", "**/*.sql", "**/openapi*.yaml", "**/openapi*.json", "bruno/**"]
---

# DB / API Contracts
- Prisma + PostgreSQL: run `npx prisma format && npx prisma validate` on schema edits; migrations via `pnpm db:generate` then `pnpm db:migrate`. Never edit existing migration SQL.
- OpenAPI + 42Crunch: keep `openapi.yaml` in sync; resolve 42Crunch diagnostics in Problems panel.
- Bruno: create a concise `.bru` per new endpoint in `bruno/`; test via `npx -y @usebruno/cli run --env local --output results.json`. Read only `results.json`.