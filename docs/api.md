# Phase 7–8 API Contract and Operations

The API is a local-first compatibility layer for repository-generated contracts plus tightly bounded private learning application state. It is versioned under `/api/v1` so future changes can preserve the stable public surface while the Markdown/YAML source model continues to evolve.

## Data flow

```text
Markdown + YAML source of truth
        ↓ deterministic generators and validators
generated JSON contracts + existing deterministic engines
        ↓ read-only public FastAPI adapter
versioned public API and responsive web client
        ↓ owner-scoped references only
PostgreSQL private application state
```

The adapter watches contract content fingerprints and refreshes cached derived structures when a generated artifact changes. It never writes Markdown, YAML, generated reports, verification fields, source fields, relationship fields, lab definitions, or cybersecurity knowledge content to PostgreSQL.

## Endpoint groups

| Group | Selected endpoints | Behavior |
| --- | --- | --- |
| Health | `GET /health`, `/ready`, `/health/knowledge`, `/health/labs`, `/health/database` | Public readiness plus separate database health |
| Entities | `GET /knowledge`, `/{type}/{id}`, `/tools`, `/vulnerabilities` | Pagination, filters, and typed detail |
| Discovery | `GET /search`, `/knowledge/{id}/related`, `/knowledge/path`, `/recommendations` | Existing deterministic engines with bounded inputs |
| Trust | `GET /trust`, `/trust/{id}`, `/review/queue` | Transparent verification, source, and review data |
| Labs | `GET /labs`, `POST /labs/{id}/instances`, `POST /lab-instances/{id}/*` | Approved local-fixture metadata and lifecycle only |
| Account | `POST /auth/register`, `/verify-email`, `/login`, `/logout`, password reset routes | Argon2id passwords, opaque server-side sessions, generic enumeration-resistant responses, and one-time token hashes |
| Private learning | `GET/PATCH/DELETE /me`, `/me/goals`, `/me/progress`, `/me/bookmarks`, `/me/notes`, `/me/recommendations` | Authenticated owner-only references, plain-text notes, deterministic explanations, and CSRF-protected mutations |

The OpenAPI document in `apps/api/openapi.json` is committed and checked for freshness. Clients should tolerate only additive fields under minor API revisions and should check explicit versioned paths rather than reverse engineering generated JSON layouts.

## Error and cache behavior

Every handler returns a stable error envelope and deliberate status code for invalid parameters, unavailable artifacts, unknown entities, invalid lab state, non-executable labs, missing authentication, CSRF failure, or unavailable private state. Search, related expansion, path finding, recommendations, comparison, health-related calls, and authentication flows have small in-process rate limits to discourage accidental expensive refresh loops. Generated data is immutable per revision; the adapter uses an artifact-content fingerprint rather than endpoint-specific stale state. Private state is never cached as public content.

## Operational safety

Run behind HTTPS in deployment, set explicit CORS origins, and terminate only with a reverse proxy that does not rewrite the documented error envelope. The public generated-contract layer remains readable when PostgreSQL is unavailable; private routes fail closed with a service-unavailable response. Sessions use secure, HttpOnly, SameSite cookies outside development, and unsafe authenticated methods require Origin checks plus a double-submit CSRF header. Lab lifecycle state is local and disposable; only authenticated completion summaries may be persisted, never raw evidence, fixture paths, or session identifiers.
