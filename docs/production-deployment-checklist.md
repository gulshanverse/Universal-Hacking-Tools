# Production Deployment Checklist

> **Current live-launch status: BLOCKED — external infrastructure prerequisites are unavailable.** This checklist is a controlled runbook; completing a repository checkbox does not assert that an external operation occurred.

## Before deployment

- [ ] Selected deployment environment has a reviewed canonical HTTPS origin, explicit DNS record, and certificate evidence.
- [ ] Production PostgreSQL is private where supported, uses separate least-privilege migration/application/backup roles where practical, and has a tested connection policy.
- [ ] Production secrets are in an approved server-side store; `make production-check` returns `READY` without revealing values.
- [ ] A verified encrypted database backup exists and its isolated restore evidence is recorded.
- [ ] Migration preflight matches the expected Alembic revision; destructive migration review is complete.
- [ ] Generated artifacts, OpenAPI, API tests, web tests, production build, and CI are current.
- [ ] Deployment commit, version, rollback candidate, external owner, and incident contact are recorded.

## During deployment

1. Freeze non-essential changes and confirm the approved commit SHA.
2. Take or verify a backup before any schema migration.
3. Run `make migration-preflight`; apply a reviewed migration through the provider’s explicit production workflow only.
4. Deploy immutable application artifacts with generated knowledge contracts read-only.
5. Verify `/api/v1/live`, `/api/v1/ready`, `/api/v1/health`, `/api/v1/health/database`, and `/openapi.json` without exposing infrastructure diagnostics.
6. Confirm explicit CORS, secure cookies over HTTPS, response security headers, and private-response cache controls.

## After deployment

Run only non-destructive smoke checks for home, search, entity detail, graph, learning path, login/session, dashboard access, public community, contributor workspace visibility, review authorization, safe-lab metadata, and database health. Do not submit production proposals, reports, moderation actions, or lab state merely to test a route. Record response status, deployment SHA, time, and any blocking result in the release evidence.

## Rollback triggers and decision

Stop promotion and collect minimal diagnostics for a failing health/readiness check, migration error, data corruption signal, authentication outage, confirmed security incident, or sustained critical server-error condition. Application rollback may be safe only when the target schema remains compatible. Database rollback is never assumed safe: use an expand/contract plan or isolated restore decision. Generated artifacts roll back with the Git commit that produced them. Never automatically destroy data or infrastructure.
