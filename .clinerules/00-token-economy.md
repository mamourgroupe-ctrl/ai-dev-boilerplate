# Token Economy (always loaded)
- Never read a whole file if search_files can locate spot; prefer replace_in_file over write_to_file.
- Silent checks: TS `npx tsc --noEmit --pretty false | head -n 25`; Py `ruff check --fix -q && ruff format -q`, `pytest -q --tb=line --maxfail=3`; JS `npx vitest run --reporter=dot`; Git `git status -s`, `git diff --stat`.
- No token spend on formatting/imports; leave to Prettier/Ruff/prisma format (0 tokens).
- Trust editor diagnostics (Prisma, 42Crunch, Pretty TS, ESLint, Pylance) before re-reading clean files.
- State in `docs/agent-state.md` (<=30 lines). At 50% context, request `/newtask`.
- Replies: terse bullets, no preamble, no explaining obvious code.
- Security: never read/print/copy `.env*`, `*.pem`, `*.key`, `id_*`. No destructive cmds without approval. No editing existing migration SQL.