# Phase 7–10 API Contract and Operations

The API is a local-first compatibility layer for repository-generated contracts plus tightly bounded private learning application state. It is versioned under `/api/v1` so future changes can preserve the stable public surface while the Markdown/YAML source model continues to evolve.

## Data flow

```text
Markdown + YAML source of truth
        ↓ deterministic generators and validators
generated JSON contracts + existing deterministic engines
        ↓ read-only public FastAPI adapter
versioned public API and responsive web client
        ↓ owner-scoped references only
PostgreSQL private application and collaboration state
```

The adapter watches contract content fingerprints and refreshes cached derived structures when a generated artifact changes. It never writes Markdown, YAML, generated reports, verification fields, source fields, relationship fields, lab definitions, or cybersecurity knowledge content to PostgreSQL. Phase 10 collaboration records are workflow evidence around a possible future repository pull request; they are never a second knowledge source.

## Endpoint groups

| Group | Selected endpoints | Behavior |
| --- | --- | --- |
| Health | `GET /health`, `/ready`, `/health/knowledge`, `/health/graph`, `/health/labs`, `/health/database` | Public readiness, generated graph metrics, and separate database health |
| Entities | `GET /knowledge`, `/{type}/{id}`, `/tools`, `/vulnerabilities` | Pagination, filters, and typed detail |
| Discovery | `GET /search`, `/discover`, `/knowledge/{id}/related`, `/knowledge/path`, `/recommendations` | Existing deterministic engines; `graph_context=true` adds labeled related matches after direct matches |
| Graph intelligence | `GET /graph/neighborhood`, `/graph/path`, `/graph/impact`, `/graph/prerequisites`, `/graph/attack-defense`, `/graph/export`, `/graph/orphans` | Generated-contract-only graph traversal with depth ≤4, nodes ≤100, edges ≤200, path length ≤25, and reviewer-only suggestions |
| Entity graph context | `GET /knowledge/{id}/prerequisites`, `/learning-route`, `/impact`, `/attack-defense` | Bounded entity-context views; optional authentication adds only the caller’s progress labels |
| Trust | `GET /trust`, `/trust/{id}`, `/review/queue` | Transparent verification, source, and review data |
| Labs | `GET /labs`, `POST /labs/{id}/instances`, `POST /lab-instances/{id}/*` | Approved local-fixture metadata and lifecycle only |
| Account | `POST /auth/register`, `/verify-email`, `/login`, `/logout`, password reset routes | Argon2id passwords, opaque server-side sessions, generic enumeration-resistant responses, and one-time token hashes |
| Private learning | `GET/PATCH/DELETE /me`, `/me/goals`, `/me/progress`, `/me/bookmarks`, `/me/notes`, `/me/recommendations`, `/me/knowledge-gaps` | Authenticated owner-only references, plain-text notes, deterministic explanations, CSRF-protected mutations, and generated-learning-path gap analysis |
| Community profiles | `GET /community`, `/community/profile/{username}`, `/me/community/profile` | Opt-in public aggregates only; private profile fields remain owner-scoped |
| Proposals and reports | `/me/contributions/*`, `/me/reports`, `/community/contributions/{id}` | Bounded plain-text proposal workflow, version history, and private reports; records are explicitly non-canonical |
| Restricted review | `/community/review/*`, `/community/maintain/*`, `/community/admin/*` | Server-enforced reviewer, maintainer, and administrator actions with audit records, conflict checks, rate limits, and CSRF on mutation |

The OpenAPI document in `apps/api/openapi.json` is committed and checked for freshness. Clients should tolerate only additive fields under minor API revisions and should check explicit versioned paths rather than reverse engineering generated JSON layouts.

## Error and cache behavior

Every handler returns a stable error envelope and deliberate status code for invalid parameters, unavailable artifacts, unknown entities, invalid lab state, non-executable labs, missing authentication, CSRF failure, or unavailable private state. Search, graph expansion, paths, recommendations, comparison, health-related calls, and authentication flows have small in-process rate limits to discourage accidental expensive refresh loops. Generated data is immutable per revision; the adapter uses an artifact-content fingerprint rather than endpoint-specific stale state. Graph responses expose a deterministic graph version and `generated_at` field; private state is never cached as public content.

## Operational safety

Run behind HTTPS in deployment, set explicit CORS origins, and terminate only with a reverse proxy that does not rewrite the documented error envelope. The public generated-contract layer remains readable when PostgreSQL is unavailable; private routes fail closed with a service-unavailable response. Sessions use secure, HttpOnly, SameSite cookies outside development, and unsafe authenticated methods require Origin checks plus a double-submit CSRF header. Lab lifecycle state is local and disposable; only authenticated completion summaries may be persisted, never raw evidence, fixture paths, or session identifiers.

Community input rejects markup and NUL characters, restricts proposal fields to controlled templates, validates safe HTTPS links, bounds pagination, and makes security reports private. Author ownership, reviewer self-review prohibition, role checks, and audit logging are enforced by the server rather than route visibility. Reputation is deterministic recognition only and cannot grant a role.

The default Git-provider adapter is unavailable by design. A maintainer may request a handoff only for an approved proposal; a missing, queued, failed, or unconfigured provider must not be described as a pull request. The web client receives no provider credential or repository write capability. Use the manual pull-request workflow in [the contribution workflow](contribution-workflow.md) until a separately configured server-side provider is available.
