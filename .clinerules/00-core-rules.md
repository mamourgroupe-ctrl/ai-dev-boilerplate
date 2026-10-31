# Core Rules

## Token Economy
- See `.clinerules/00-token-economy.md` (always loaded). Silent checks, no full-file reads, replace_in_file.

## Workflow
1. PLAN MODE: analyze + plan before coding.
2. MEMORY BANK: read `memory-bank/activeContext.md` + `systemPatterns.md` at conversation start.
3. SUBAGENTS: delegate exploration; trigger "Use subagents to explore ...".
4. ACT MODE: implement per architecture rules.
5. VERIFICATION: run relevant tests/Bruno.

## Security (HARD)
- Never read/print/copy `.env*`, `*.pem`, `*.key`, `id_*`.
- Never edit existing migration SQL; new migrations only.
- No destructive DB/shell cmds without approval. No secrets/agent dirs committed.

## Git
- No `git add/commit/push` unless requested. Keep turbo managed block intact.

## Model usage
- Strong model for planning; faster/cheaper for execution. Prefer concise results.