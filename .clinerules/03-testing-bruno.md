# API Specs & Testing

## OpenAPI
- Any new route must have `@ApiOperation` and `@ApiResponse` decorators.
- All new endpoints must conform to the OpenAPI spec (see `42Crunch.vscode-openapi`).

## Bruno
- After creating a new endpoint, generate the corresponding Bruno `.bru` file in the `bruno/` directory.
- Verify endpoints using the Bruno CLI before confirming the task (see `bruno-api-client.bruno`).

## Bruno CLI (token optimization)
- Run tests with `npx @usebruno/cli run --env local --output results.json` (do not assume a global `bru` command exists).
- Read only `results.json` to check failures; do NOT print full HTTP responses in chat.

## Verification loop (run before finishing any task)
From repo root:
- `pnpm lint` · `pnpm typecheck` · `pnpm test` · `pnpm build`
Scoped:
- `pnpm --filter @rihal/api lint|typecheck|test`
- `pnpm --filter @rihal/database typecheck|test`
For DB changes: `pnpm db:generate` then `pnpm db:migrate`.