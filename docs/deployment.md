# Phase 7 Deployment Notes

Phase 7 consists of two deployable processes: the FastAPI adapter in `apps/api` and the Next.js client in `apps/web`. Both require the repository’s generated JSON artifacts to be present and current. Deploying stale or partially generated artifacts is unsupported; run the existing generator and freshness checks first.

## Required configuration

| Service | Setting | Purpose |
| --- | --- | --- |
| API | `UHT_ALLOWED_ORIGINS` | Explicit comma-separated public web origins |
| API | `UHT_LAB_STATE_DIR` | Ephemeral local fixture state root, never a production-data mount |
| Web | `NEXT_PUBLIC_API_URL` | Public versioned API base ending in `/api/v1` |
| Web | `NEXT_PUBLIC_SITE_URL` | Canonical public web origin |

Terminate TLS at a trusted platform or reverse proxy. The API must not be exposed with wildcard CORS, debug mode, stack-trace errors, a writable content mount, privileged containers, host networking, or durable lab evidence. The web application has no account data or database migrations.

## Deployment order

First generate and validate repository artifacts. Next deploy the API with the generated files read-only. Confirm `/api/v1/health`, `/api/v1/ready`, `/openapi.json`, and CORS for the web origin. Then build and deploy the web application with the corresponding public API URL. Finally run the browser lifecycle smoke test only against a dedicated disposable lab state root.

## Explicitly deferred

Accounts, progress synchronization, database persistence, shared lab queues, remote execution, public write APIs, third-party analytics, telemetry, AI assistants, embeddings, and semantic ranking are outside Phase 7. Add them only under a separately reviewed phase with a threat model, privacy review, migration plan, and rollback strategy.
