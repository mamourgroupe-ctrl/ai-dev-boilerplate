# NestJS 11 Architecture

## Structure
- Follow Domain-Driven Design (DDD). Use Modules, Controllers, and Services strictly.
- Controllers thin; business logic in services. No business logic in controllers.
- TypeScript strict mode (`strictNullChecks`, `noImplicitAny`). No `any` without justification.

## DTOs & Validation
- Always use `class-validator` and `class-transformer` for incoming payloads. Never trust user input.
- Apply `ValidationPipe` globally or at the controller level.
- Apply `AuthGuard` (JWT) at controller level where required.

## Multi-tenancy (Controller layer)
- Resolve `tenantId` from signed JWT claims only — never from request body.
- Never accept `tenantId` in DTOs or query params from clients.

## Redis
- Use the injected Redis client for caching/sessions only. Do not use it as a primary DB.

## Paths
- Use `path.join`/`path.resolve`; never hardcode separators (Windows/WSL compatible).