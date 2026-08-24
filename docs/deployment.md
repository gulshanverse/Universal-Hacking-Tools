# Phase 11 Deployment Notes

The platform consists of a FastAPI adapter in `apps/api`, a Next.js client in `apps/web`, and a PostgreSQL application-state database. The API and web client require the repository’s generated JSON artifacts to be present and current. Deploying stale or partially generated artifacts is unsupported; run the existing generator and freshness checks first.

## Required configuration

| Service | Setting | Purpose |
| --- | --- | --- |
| API | `UHT_ALLOWED_ORIGINS` and `UHT_TRUSTED_HOSTS` | Explicit production HTTPS origins and host names; never wildcard credentialed origins |
| API | `UHT_LAB_STATE_DIR` | Ephemeral local fixture state root, never a production-data mount |
| API | `DATABASE_URL` | PostgreSQL connection for private application state only; never a knowledge-content source |
| API | `SESSION_SECRET` | Long random secret used to hash opaque server-side sessions |
| API | `CSRF_SECRET` | Long random secret used to bind double-submit CSRF tokens |
| API | `UHT_ENVIRONMENT`, secure-cookie, request/pool/timeout controls | Set to `production` only with explicit PostgreSQL, absolute local-lab path, non-placeholder secrets, HTTPS origins, trusted hosts, and secure cookies |
| Web | `NEXT_PUBLIC_API_URL` | Public versioned API base ending in `/api/v1` |
| Web | `NEXT_PUBLIC_SITE_URL` | Canonical public web origin |

Terminate TLS at a trusted platform or reverse proxy. The API must not be exposed with wildcard CORS, debug mode, stack-trace errors, a writable content mount, privileged containers, host networking, or durable lab evidence. Enforce HTTPS and secure cookie mode outside development. The API refuses production startup with development defaults, non-HTTPS origins, missing trusted hosts, missing PostgreSQL configuration, non-absolute explicit lab state path, or unsafe session/CSRF secrets. PostgreSQL holds only private application and collaboration state; no Markdown/YAML or generated cybersecurity knowledge is copied into database tables. See the [production architecture](production-architecture.md), [secrets](production-secrets.md), [deployment checklist](production-deployment-checklist.md), and [readiness report](production-readiness.md).

## Deployment order

First generate and validate repository artifacts. Back up the private-state database and test migration upgrade and downgrade on a restore. Apply `alembic upgrade head` before starting the new API version, then deploy the API with generated files read-only. Confirm `/api/v1/health`, `/api/v1/health/database`, `/api/v1/ready`, `/openapi.json`, and CORS for the web origin. Then build and deploy the web application with the corresponding public API URL. Finally run account, multi-user privacy, and browser lifecycle smoke tests only against a dedicated disposable lab state root.

## Database-degraded behavior and deferred operations

If PostgreSQL is unavailable, generated-contract knowledge endpoints continue serving read-only data and the database health/readiness response reports degradation. Authenticated private reads and writes fail closed with a service-unavailable response; the API never queues private writes. Multi-instance shared rate limiting, external production email delivery operations, remote execution, public write APIs, third-party analytics, telemetry, AI assistants, embeddings, and semantic ranking remain outside this implementation.
