# Phase 11 Production Readiness

> **Public go-live decision: BLOCKED.** The repository can implement and validate production controls, but no domain, DNS, TLS verification, public deployment, production PostgreSQL, email provider, backup/restore source, hosted monitoring, or production Git provider is configured in the repository.

The machine-readable companion is [`generated/production-readiness.json`](../generated/production-readiness.json). Its `BLOCKED` decision is deliberate: a repository control cannot override a critical external infrastructure prerequisite.

## Evidence model

`not-configured` means the repository has no configuration evidence. `configured` means versioned configuration or runbook exists. `validated` means a local or CI check has passed. `verified` is reserved for documented evidence from the actual target environment. `blocked` means an external prerequisite is unavailable.

## External blocker table

| Requirement | Status | Evidence | Action |
| --- | --- | --- | --- |
| Domain and DNS | `blocked` | No canonical host or DNS record is configured. | Select and verify a domain; document redirect and `www` behavior. |
| TLS | `blocked` | No public certificate or HTTPS endpoint is available. | Configure platform TLS, renewal, HTTPS redirect, secure cookies, and HSTS verification. |
| PostgreSQL | `blocked` | Development compose is not production infrastructure. | Provision private PostgreSQL, least-privilege roles, encryption/TLS where supported, and migration evidence. |
| Email | `blocked` | Development in-memory backend is not production delivery. | Select and verify a provider only if verification/reset delivery is required. |
| Git provider | `not-configured` | Safe unavailable adapter and manual PR fallback exist. | Enable only after least-privilege server credential and audit design review. |
| Deployment | `blocked` | No hosting provider or live URL is configured. | Select provider; implement approved deploy and post-deploy checks. |
| Backups | `blocked` | No provider backup/retention/restore evidence exists. | Configure encryption, access, retention, and isolated restore drill. |
| Monitoring | `blocked` | Structured logs exist in code; no hosted sink/alerts exist. | Configure minimal privacy-safe log/alert pipeline and response ownership. |

## Repository readiness versus public launch

Repository readiness requires code, tests, generated artifacts, docs, migration preflight, and release processes to pass. A public launch additionally requires verified external evidence. The former may be **GO WITH NON-BLOCKING GAPS** only after all repository checks pass; the latter remains **BLOCKED** while any critical external row above is blocked.

## Required production checks

Use `make production-check` only with explicitly supplied production environment variables. It validates configuration and locally available artifacts without printing secrets or provisioning resources. Use `make migration-preflight` against a selected database only after a reviewed backup. Use `make restore-verify` only against an operator-restored isolated test/staging database with `UHT_RESTORE_DRILL_TARGET=isolated`.

## Performance and smoke evidence

No staging or production target exists for safe performance measurements, load testing, or live smoke tests; those are `blocked`. When a target exists, measure home, search, entity, graph, login, dashboard, and community paths with safe synthetic traffic. Production smoke checks must be read-only or use intentionally isolated test accounts; they must not create reports, proposals, moderation actions, remote labs, or destructive state.
