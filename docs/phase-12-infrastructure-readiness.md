# Phase 12A Infrastructure Readiness

> **Decision: repository planning is complete; public deployment remains BLOCKED.** This document inspects the Phase 1–11 repository only. It does not create an account, provider project, database, domain, DNS record, certificate, secret, deployment, or infrastructure resource.

## Current repository state

The repository contains a Next.js 15 web application, a FastAPI application, generated JSON contracts for all public cybersecurity knowledge, and PostgreSQL-only private application/community state. Markdown/YAML and generated JSON remain authoritative knowledge sources; PostgreSQL must never become a second knowledge corpus. The current production-readiness artifact lists DNS, TLS, production PostgreSQL, deployment, email delivery, backup/restore evidence, and hosted monitoring as external blockers. [Production architecture](production-architecture.md) and [production readiness](production-readiness.md) remain the repository authority for that distinction.

The only Compose definition is a local development PostgreSQL 16 service. There is no Dockerfile, production Compose topology, provider manifest, reverse-proxy configuration, deployment account, custom domain, certificate, or live service configuration. The only active workflow validates the repository, migrations, API, and web build on GitHub Actions; it does not deploy.

| Repository component | Status | Infrastructure implication |
| --- | --- | --- |
| Generated knowledge/graph contracts | VERIFIED | Include committed `generated/` artifacts in each immutable API release; no graph database is needed. |
| FastAPI `/api/v1` application | AVAILABLE | Requires a long-running Python HTTP service reachable over HTTPS through an approved host/proxy. |
| Next.js web application | AVAILABLE | Requires a Node-capable platform, not a static-file-only host, because the app has dynamic/SSR routes. |
| PostgreSQL private state | BLOCKED | A managed or operator-maintained PostgreSQL 16-compatible service is required before public account/community features can work. |
| Local safe-lab state | AVAILABLE | Requires a writable, ephemeral, non-public absolute filesystem directory and a single API instance initially. |
| Email delivery | BLOCKED | Only an in-memory development adapter exists; production verification/reset delivery has no implementation or provider configuration. |
| Git-provider handoff | NOT CONFIGURED | The server-side adapter fails safely; manual pull requests remain the required fallback. |

## Required production components

The smallest viable topology has a canonical HTTPS frontend origin, a separate canonical HTTPS API origin, one API process, PostgreSQL, server-side secret storage, a transactional-email integration if registration/reset is enabled, a backup mechanism, and basic external availability monitoring. The public request path is browser → DNS/TLS/edge → Next.js and FastAPI → generated contracts and PostgreSQL. Do not add a vector database, graph database, remote lab runner, browser-side secret, or GitHub write credential.

The initial deployment should keep a **single API replica**. Rate limiting, local-lab ownership, and safe-lab lifecycle state are process-local; horizontal scaling would require a separately reviewed shared limiter and state design. The API process needs a writable `UHT_LAB_STATE_DIR`, but it must be treated as ephemeral fixture state—not as an evidence, upload, or user-data store.

## Frontend requirements

| Item | Exact requirement |
| --- | --- |
| Runtime | Node.js **22**, pnpm **11.21.0**; these versions are validated in CI. |
| Install | `cd apps/web && pnpm install --frozen-lockfile` |
| Production configuration check | `UHT_ENVIRONMENT=production NEXT_PUBLIC_API_URL=https://api.example.invalid/api/v1 NEXT_PUBLIC_SITE_URL=https://app.example.invalid pnpm production-check` using actual chosen public URLs at deployment time. |
| Build | `UHT_ENVIRONMENT=production NEXT_PUBLIC_API_URL=https://<api-host>/api/v1 NEXT_PUBLIC_SITE_URL=https://<web-host> NODE_ENV=production pnpm build` |
| Start | `pnpm start -- -H 0.0.0.0 -p "$PORT"` where the provider supplies `PORT`; use `3000` only when no provider port is supplied. |
| Public configuration | `NEXT_PUBLIC_API_URL` must be a credential-free HTTPS URL ending in `/api/v1`; `NEXT_PUBLIC_SITE_URL` must be the canonical HTTPS web URL. Both values are compiled into the browser bundle. |
| Security expectation | The configured API origin becomes the browser CSP `connect-src` origin. Dashboard/review/admin responses are private/no-store and noindex. HSTS is emitted only when `UHT_ENVIRONMENT=production`. |

The frontend cannot be deployed to an HTML-only static host unless its dynamic Next.js requirements are independently supported. The free Vercel Hobby plan is for personal/small-scale use and has usage and eligibility limits; it can be considered only after the account holder confirms those terms. [1]

## API requirements

| Item | Exact requirement |
| --- | --- |
| Runtime | Python **3.12** is validated in CI; production should use the same minor version. |
| Install | `python3 -m pip install -r apps/api/requirements.txt` |
| Build step | No separate compile artifact is defined. Run `PYTHONPATH=apps/api:. python3 apps/api/scripts/check_openapi.py` and the preserved validation suite before release. |
| Start | `PYTHONPATH=apps/api:. python3 -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT"`; do not use the local-only Make target’s `127.0.0.1` bind in a provider container/service. |
| Read-only release input | Repository root and `generated/` contracts must be available read-only to the API process. |
| Health/smoke endpoints | `GET /api/v1/live`, `/api/v1/ready`, `/api/v1/health`, and `/api/v1/health/database`; `GET /openapi.json` is also expected. |
| Process model | One API instance at first; no production remote lab execution, uploads, arbitrary command execution, or shared in-memory assumptions. |

The API uses FastAPI, Uvicorn, SQLAlchemy 2, Alembic, Argon2id, and psycopg 3.2. Production startup rejects a non-PostgreSQL database URL, missing/non-HTTPS CORS origins, missing trusted hosts, insecure cookies, missing/short placeholder session or CSRF secrets, and an implicit lab-state directory.

## PostgreSQL requirements

PostgreSQL **16** is the exact compatibility baseline: local Compose and CI both use `postgres:16-alpine`. Select a managed PostgreSQL 16 service where possible. The database stores only private accounts, opaque session records, learning state, safe-lab summaries, and controlled community workflow/audit state. It must not receive raw Markdown/YAML or generated knowledge as canonical tables.

| Requirement | Needed before production migration |
| --- | --- |
| Connectivity | Server-side, credentialed PostgreSQL URL using the SQLAlchemy psycopg scheme; do not expose it to the web build. |
| Access | Least-privilege application identity; separate migration/backup identities where provider capabilities allow. |
| Transport/storage | Provider TLS and encrypted storage must be verified by the operator. |
| Capacity | Configure API pool defaults deliberately: pool size 5, overflow 5, timeout 30 seconds, statement timeout 30 seconds unless measured evidence justifies a change. |
| Migration | `cd apps/api && PYTHONPATH=. alembic upgrade head` after a reviewed backup and `make migration-preflight`; do not use `db-reset` or downgrade as a production deployment action. |
| Seed | **No production seed.** `seed_development.py` rejects production, uses fake `*.example.test` identities, and is development/test-only. A controlled first-administrator/bootstrap procedure is a Phase 12B governance prerequisite, not an instruction to run development seeding. |

## Authentication/email requirements

The application has Argon2id passwords, opaque HttpOnly session cookies, CSRF protection, verified-email and reset flows. Secure cookies require a canonical HTTPS frontend/API arrangement with credentialed CORS. The current `DevelopmentEmailService` only retains verification/reset tokens in memory and makes no network call. Therefore email is **BLOCKED** for a public deployment; setting `UHT_EMAIL_BACKEND` alone does not create a production sender.

Phase 12B must select, implement, and test a server-only transactional-email adapter; verify a sender domain; keep provider credentials server-side; confirm token redaction; and test delivery, failure handling, rate limits, and account-enumeration resistance. A free Resend plan currently documents 3,000 transactional emails per month with a 100-per-day ceiling, which may suit a non-production pilot but must be rechecked at selection time. [5]

## Secrets inventory

No actual secret values belong in the repository, browser bundle, CI output, health endpoint, or this plan. `DATABASE_URL`, `SESSION_SECRET`, and `CSRF_SECRET` are the mandatory production secrets. Generate separate long random session and CSRF values and expect their rotation to invalidate existing sessions/tokens as documented in [production secrets](production-secrets.md). A Git-provider credential is optional and remains absent; it must not be created merely for Phase 12A.

## DNS requirements

Before deployment, the operator must choose—not invent—one canonical public web hostname and one API hostname (or an approved same-origin routing design). Create DNS records only after the selected hosting providers present the required targets. Configure one canonical redirect policy and add both eventual public hosts to `UHT_TRUSTED_HOSTS`; set the canonical web HTTPS origin exactly in `UHT_ALLOWED_ORIGINS`. No DNS record is configured now.

## TLS requirements

TLS is an external prerequisite. The selected frontend/API hosts must provide verified HTTPS before production cookies or CORS are enabled. Confirm certificate issuance/renewal, HTTP-to-HTTPS redirect behavior, HSTS delivery, and browser access to the exact API HTTPS origin. The repository does not create certificates or terminate TLS itself.

## Backup requirements

Public production requires encrypted PostgreSQL backups, restricted backup access, documented retention, and a recorded restore test. Free Render PostgreSQL is unsuitable for this requirement because its documented free database expires after 30 days and lacks backups; its free web service also spins down and loses local filesystem state. [2] The current repository has only a runbook and a guarded verifier; no backup provider, policy, or evidence exists.

## Monitoring requirements

The API logs UTC timestamp, request ID, route, method, status, duration, and environment to process output while excluding credentials, database URLs, payloads, notes, reports, and raw evidence. A deployment operator must choose a restricted-access log sink/retention policy and alert owner. Monitor at least the canonical web URL and API `/api/v1/live`, `/api/v1/ready`, and `/api/v1/health/database` without authentication payloads. UptimeRobot documents a free plan with 50 monitors and five-minute checks, but commercial suitability and notification requirements must be reconfirmed by the account holder. [6]

## GitHub integration requirements

GitHub repository CI is already available and validates the codebase; deployment credentials must not be added to it in Phase 12A. The application Git-provider handoff is intentionally unavailable. If a future GitHub App/integration is enabled, it requires a separately reviewed server-only secret, least privilege, audit logging, failure-safe behavior, and manual pull-request fallback. A real token, repository write, PR creation, merge action, or GitHub provider resource is **not** a Phase 12A action.

## Safe-lab production boundary

Safe labs stay local synthetic fixtures. The API permits only predefined validated tasks, uses a server-only absolute `UHT_LAB_STATE_DIR`, limits active local sessions in process, and must not expose a terminal, upload, target field, remote command, scan, exploit, or durable raw evidence. The selected host must allow one writable ephemeral fixture directory and must not attach it to public/static serving. If a platform has an ephemeral filesystem, lab state is intentionally lost on restart, redeploy, or scale-down; that is acceptable only for the documented disposable fixture model.

## Free/low-cost deployment strategy

### Strategy A — free evaluation only; not a public production recommendation

Use a hosted Next.js evaluation tier plus a free Python API/database tier only to prove provider wiring with fake accounts and no production promise. Vercel Hobby may be eligible for personal, non-commercial web evaluation. [1] Render offers free Python web services and Postgres, but its own documentation says not to use free instances for production; free services sleep after 15 minutes, and free Postgres has no backup and expires. [2] Neon Free provides scale-to-zero PostgreSQL with 0.5 GB storage, a six-hour history window, one manual snapshot, and no scheduled snapshots; it does not meet this repository’s backup/restore go-live requirement. [3]

### Strategy B — recommended Phase 12B low-cost production candidate

Keep the web/API/database split, but choose providers only after the operator confirms current terms, region, cost ceiling, ownership, backup, and account eligibility. A practical candidate is a Node-capable frontend host plus a single always-available or acceptably cold-started Python service and a managed PostgreSQL plan with scheduled backups/restore evidence. Use Vercel only if its Hobby personal/non-commercial restriction and usage limits fit; otherwise choose a paid frontend runtime or a single provider. [1] For PostgreSQL, Neon Launch has configurable paid availability plus scheduled snapshots/history, while Supabase Pro documents daily backups; neither is configured or endorsed until the operator evaluates data residency, access, cost, and backup evidence. [3] [4]

### Strategy C — single-provider low-operations alternative

Select one provider that can run Node and Python services plus managed PostgreSQL, TLS, logs, and backups in a compatible region. This reduces cross-provider CORS/DNS complexity but must still provide a Node runtime for the dynamic web app, an API process with a writable ephemeral lab directory, secret injection, PostgreSQL backups, and health visibility. Railway and Fly.io document FastAPI deployment methods, but this repository currently has no provider manifest or Dockerfile; adding one is a Phase 12B design decision, not a Phase 12A change. [7] [8]

## Provider selection criteria

| Criterion | Minimum acceptable answer before selection |
| --- | --- |
| Web runtime | Runs Next.js dynamic/SSR routes with Node 22 and supports build-time public environment values. |
| API runtime | Runs one Python 3.12/Uvicorn process with configurable `PORT`, private env injection, and read-only repository/generated artifacts. |
| Database | PostgreSQL 16-compatible, TLS, limited-access credentials, encrypted backups, retention, and documented isolated restore capability. |
| Networking | Canonical HTTPS web/API URLs, CORS support for credentialed requests, custom-domain/DNS process, certificate renewal, and request-size/timeout compatibility. |
| Persistence | Explicitly understands ephemeral safe-lab state; does not rely on API filesystem for database, uploads, or evidence. |
| Operations | Privacy-safe logs, restricted access, health checks, alert channel, deployment rollback path, and spend controls. |
| Account terms | Free-tier eligibility, commercial-use limits, sleeping behavior, quotas, backup availability, expiry, and cost-overrun policy are confirmed by the user at selection time. |

## Exact environment-variable matrix

| Variable | Required | Public/Secret | Used By | Production Source | Status |
|---|---|---|---|---|---|
| `UHT_ENVIRONMENT=production` | Yes | Server-only | API and web build/runtime | Deployment runtime configuration | NOT CONFIGURED |
| `DATABASE_URL` | Yes | Secret | API | Managed PostgreSQL server-side secret store | BLOCKED |
| `SESSION_SECRET` | Yes | Secret | API | Server-side secret store; independent random value, at least 32 characters | BLOCKED |
| `CSRF_SECRET` | Yes | Secret | API | Server-side secret store; independent random value, at least 32 characters | BLOCKED |
| `UHT_ALLOWED_ORIGINS` | Yes | Server-only | API CORS | Exact canonical web HTTPS origin, no trailing path/wildcard | NOT CONFIGURED |
| `UHT_TRUSTED_HOSTS` | Yes | Server-only | API trusted-host middleware | Exact API host and any approved API aliases | NOT CONFIGURED |
| `UHT_LAB_STATE_DIR` | Yes | Server-only | API safe labs | Absolute writable ephemeral fixture path supplied by API host | NOT CONFIGURED |
| `UHT_SECURE_COOKIES=true` | Yes | Server-only | API cookies | Deployment runtime configuration after HTTPS verification | NOT CONFIGURED |
| `NEXT_PUBLIC_API_URL` | Yes | Public build-time | Web browser/CSP | Exact credential-free API HTTPS base ending `/api/v1` | NOT CONFIGURED |
| `NEXT_PUBLIC_SITE_URL` | Yes | Public build-time | Web metadata/build | Exact canonical web HTTPS origin | NOT CONFIGURED |
| `UHT_BUILD_VERSION` | Recommended | Server-only metadata | API health | Release version/commit process; no secrets | AVAILABLE |
| `UHT_BUILD_COMMIT` | Recommended | Server-only metadata | API health | Exact approved Git SHA; no secrets | AVAILABLE |
| `UHT_ENABLE_DOCS=false` | Recommended | Server-only | API | Runtime configuration for public production | NOT CONFIGURED |
| `UHT_LOG_LEVEL=INFO` | Recommended | Server-only | API logging | Runtime configuration with provider log-retention policy | NOT CONFIGURED |
| `UHT_SESSION_TTL_SECONDS` | Optional | Server-only | API authentication | Reviewed security policy; default 1,209,600 seconds | AVAILABLE |
| `UHT_SESSION_IDLE_SECONDS` | Optional | Server-only | API authentication | Reviewed security policy; default 86,400 seconds | AVAILABLE |
| `UHT_MAX_REQUEST_BYTES`, `UHT_MAX_URL_LENGTH`, `UHT_MAX_HEADER_BYTES` | Optional | Server-only | API request boundary | Defaults or measured provider-compatible limits | AVAILABLE |
| `UHT_DATABASE_POOL_SIZE`, `UHT_DATABASE_MAX_OVERFLOW`, `UHT_DATABASE_POOL_TIMEOUT_SECONDS`, `UHT_DATABASE_STATEMENT_TIMEOUT_MS` | Optional | Server-only | API/DB | Defaults or measured database-capacity limits | AVAILABLE |
| `UHT_EMAIL_BACKEND` | Not sufficient | Server-only | Development template only | Requires a new reviewed production email implementation and provider secret design | BLOCKED |
| Git-provider credential | Optional | Secret | Future server-only adapter | Only after separate GitHub integration review | NOT CONFIGURED |

`UHT_API_HOST`, `UHT_API_PORT`, and provider `PORT` appear in development guidance, but the production Uvicorn command should bind `0.0.0.0` and use the provider-supplied port. They are not browser values or secrets. Do not create provider-specific variables until a provider is selected.

## External prerequisites

| Requirement | Status | Why Needed | Action |
|---|---|---|---|
| Frontend runtime provider | NOT CONFIGURED | Dynamic Next.js service/build and canonical public web URL | User selects an eligible provider and account; do not deploy in Phase 12A. |
| API runtime provider | NOT CONFIGURED | Python 3.12/Uvicorn process, health checks, secret injection, ephemeral lab directory | User selects a provider supporting one initial API instance. |
| PostgreSQL 16-compatible service | BLOCKED | Private auth, learning, community, audit, and report state | User creates a database only in Phase 12B after backup/access review. |
| Production secret store | BLOCKED | Database/session/CSRF and future provider credentials | User enables provider-side secret storage and supplies values privately in Phase 12B. |
| Canonical web/API hostnames | NOT CONFIGURED | Exact CORS, trusted hosts, public URLs, and user-facing links | User chooses names; no DNS records in Phase 12A. |
| DNS records | BLOCKED | Route canonical names to selected providers | User creates/verifies records in Phase 12B. |
| TLS certificates/redirects | BLOCKED | Secure cookies, HTTPS-only CORS, HSTS, public browser access | User/provider verifies issuance, renewal, and redirects in Phase 12B. |
| Transactional email provider and adapter | BLOCKED | Verified-email and password-reset delivery | Select and implement/test a server-only adapter in a separately reviewed Phase 12B change. |
| Encrypted backups and restore evidence | BLOCKED | Data recovery and deployment safety | Configure provider backups, retention, access, and an isolated restore drill. |
| Hosted logs/alerts | BLOCKED | Outage/security visibility and response ownership | Choose restricted log sink, monitor endpoints, define alert recipient/retention. |
| GitHub application/provider integration | NOT CONFIGURED | Optional approved-proposal handoff only | Retain manual PR fallback unless a separately reviewed server-side integration is added. |
| Production admin bootstrap policy | BLOCKED | Development seed is prohibited; moderation requires authorized roles | Define a reviewed, auditable initialization process without fake seed accounts. |

## Phase 12B prerequisites

Before any actual deployment begins, the user must personally select providers and regions, accept terms/pricing, create accounts, choose canonical web/API hostnames, decide whether the project is eligible for any free tier, and provide account/provider access only through approved channels. The user must also choose database ownership, backup retention, recovery owner, log/alert recipient, transactional email provider, and a controlled administrator bootstrap policy.

What can be automated after those decisions are supplied: repeatable environment validation, dependency installation, artifact checks, migration preflight, reviewed migration execution against the chosen database, application build/start, health and header checks, non-destructive smoke checks, and CI evidence capture. What requires account/provider access: provider project creation, billing/terms acceptance, secret entry, database provisioning, DNS, TLS, domain purchase/assignment, email-domain verification, backups, monitoring recipients, and any GitHub App configuration.

## Phase 12B recommended next step

Hold a provider-selection review before any provisioning. Choose one documented **evaluation** topology and one **go-live** topology, record current provider terms/cost limits, assign an operational owner, and approve the external prerequisite table. Only then should a separate Phase 12B task create a minimal staging environment, add narrowly scoped deployment configuration if needed, verify backups/email/monitoring, and seek explicit confirmation before a public deployment.

## References

[1]: https://vercel.com/docs/plans/hobby "Vercel Hobby Plan"
[2]: https://render.com/docs/free "Render Deploy for Free"
[3]: https://neon.com/pricing "Neon Pricing Plans"
[4]: https://supabase.com/pricing "Supabase Pricing"
[5]: https://resend.com/docs/knowledge-base/what-is-resend-pricing "Resend Transactional Email Pricing"
[6]: https://uptimerobot.com/pricing/ "UptimeRobot Plans and Pricing"
[7]: https://docs.railway.com/guides/fastapi "Railway Deploy a FastAPI App"
[8]: https://fly.io/docs/python/frameworks/fastapi/ "Fly.io Run a FastAPI App"
