# Production Architecture and External Prerequisites

This document records the architecture supported by the repository and separates it from infrastructure that has not been configured. It is not a deployment claim.

## Architecture status

| Layer | Required for a public service | Repository configuration | External state |
| --- | --- | --- | --- |
| Source and generated contracts | Git review and deterministic generators | `configured` | `validated` by repository checks, not a hosting claim |
| API | FastAPI process serving `/api/v1` behind HTTPS | `configured` | `not-configured` for public hosting |
| Web | Next.js production build served from a canonical HTTPS origin | `configured` | `not-configured` for public hosting |
| Database | PostgreSQL for private state with non-public connectivity | Development compose only | `blocked` — production provider and credentials unavailable |
| Edge | DNS, TLS, redirect policy, request limits, optional WAF/CDN | No provider-specific configuration | `blocked` — external prerequisite unavailable |
| Observability | Privacy-safe structured application logs and a configured sink/alert policy | Application-side work planned | `blocked` for hosted sink/alerting |
| Backup and recovery | Encrypted backup, access control, retention, isolated restore evidence | Runbooks only | `blocked` — provider prerequisite unavailable |

## Environment model

| Environment | Purpose | Data and access policy |
| --- | --- | --- |
| `development` | Local implementation and non-production fixtures | Development-only secrets and seed workflow may be used only here. |
| `test` | Isolated automated validation | Disposable database and explicitly fake accounts only. |
| `staging` | Pre-production integration and smoke verification | `blocked` until an external staging environment is provisioned. It must not share production secrets or data. |
| `production` | Public service | Must fail startup if production secrets or critical configuration are absent; production-only infrastructure evidence is required before launch. |

## Required request path

```text
Browser
  -> DNS / canonical HTTPS host (external prerequisite)
  -> edge or reverse proxy with TLS and request protection (external prerequisite)
  -> Next.js web client and FastAPI API
  -> generated repository contracts for public knowledge
  -> PostgreSQL only for private application and collaboration state
  -> encrypted backup / isolated recovery process (external prerequisite)
```

The API and web processes may be deployed together or separately only after the selected platform’s configuration is reviewed. The repository does not prescribe a provider and does not provision a DNS record, certificate, database, backup, cache, WAF, email service, GitHub credential, or monitor.

## Deferred and optional components

An edge WAF, CDN, hosted log sink, shared rate-limit store, production email provider, and real GitHub provider are optional integrations. They must be justified by the selected deployment topology and abuse model. The Git provider is intentionally unavailable until a server-only, least-privilege configuration is separately reviewed; manual pull requests remain the safe fallback.

## Go-live boundary

The repository can become **repository-ready** through code, documentation, CI, local production checks, and rehearsed isolated workflows. A live public launch remains **blocked** until the required external resources and their verification evidence are available. See [production readiness](production-readiness.md) for the current evidence model.
