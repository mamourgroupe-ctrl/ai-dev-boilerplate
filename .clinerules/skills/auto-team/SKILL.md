---
name: auto-team
description: Orchestrates local/free agents for a 4-stage token-efficient pipeline: surgical scout, delegated summaries, contract-first implementation, state update.
---

# Auto-Team Pipeline (token-efficient)
(a) Surgical scout: `git status -s` + read `docs/agent-state.md`; use `context7` only if needed.
(b) Delegate: use free local agents (`opencode run`, `ollama run qwen2.5:3b`) for repetitive template generation, `bruno/*.bru` test files, and summarizing long outputs; require <=15 lines back to Cline (0 API tokens).
(c) Implement across contracts: Prisma -> OpenAPI/42Crunch -> code (NestJS/Next.js/Python) -> Bruno/Vitest/Pytest, zero diagnostics.
(d) Update `docs/agent-state.md` with <=10 lines and deliver result.

Rules: terse replies, no full-file reads when search suffices, use replace_in_file, silent checks only.