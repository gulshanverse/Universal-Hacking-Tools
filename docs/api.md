# Phase 7 API Contract and Operations

The Phase 7 API is a local-first compatibility layer for the repository’s generated contracts. It is versioned under `/api/v1` so future changes can preserve the stable public surface while the Markdown/YAML source model continues to evolve.

## Data flow

```text
Markdown + YAML source of truth
        ↓ deterministic generators and validators
generated JSON contracts + existing deterministic engines
        ↓ read-only FastAPI adapter
versioned API and responsive web client
```

The adapter watches contract content fingerprints and refreshes cached derived structures when a generated artifact changes. It never writes Markdown, YAML, generated reports, verification fields, source fields, relationship fields, or lab definitions.

## Endpoint groups

| Group | Selected endpoints | Behavior |
| --- | --- | --- |
| Health | `GET /health`, `/ready`, `/health/knowledge`, `/health/labs` | Readiness and generated health views |
| Entities | `GET /knowledge`, `/{type}/{id}`, `/tools`, `/vulnerabilities` | Pagination, filters, and typed detail |
| Discovery | `GET /search`, `/knowledge/{id}/related`, `/knowledge/path`, `/recommendations` | Existing deterministic engines with bounded inputs |
| Trust | `GET /trust`, `/trust/{id}`, `/review/queue` | Transparent verification, source, and review data |
| Labs | `GET /labs`, `POST /labs/{id}/instances`, `POST /lab-instances/{id}/*` | Approved local-fixture metadata and lifecycle only |

The OpenAPI document in `apps/api/openapi.json` is committed and checked for freshness. Clients should tolerate only additive fields under minor API revisions and should check explicit versioned paths rather than reverse engineering generated JSON layouts.

## Error and cache behavior

Every handler returns a stable error envelope and deliberate status code for invalid parameters, unavailable artifacts, unknown entities, invalid lab state, or non-executable labs. Search, related expansion, path finding, recommendations, comparison, and health-related calls have small in-process rate limits to discourage accidental expensive refresh loops. Generated data is immutable per revision; the adapter uses an artifact-content fingerprint rather than endpoint-specific stale state.

## Operational safety

Run behind HTTPS in deployment, set explicit CORS origins, and terminate only with a reverse proxy that does not rewrite the documented error envelope. The service does not need a database, object storage, third-party API key, user account system, or background worker. Lab lifecycle state is local and disposable; it should not be mounted to production data or a durable shared path.
