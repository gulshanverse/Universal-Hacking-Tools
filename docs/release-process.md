# Release Process

The repository’s release process is Git-reviewed and evidence-driven. It does not grant an automated deployment path, configure a hosting environment, or permit untrusted pull requests to access deployment secrets.

## Controlled flow

```text
feature branch -> pull request -> validation CI -> review -> merge
-> immutable build -> staging smoke test (when configured)
-> approved production deployment (when configured) -> health verification
```

All repository changes must preserve Markdown/YAML plus generated JSON as cybersecurity knowledge authority. Application-state migrations must be reviewed separately from content changes. The optional Git-provider adapter is PR-only and never auto-merges canonical knowledge.

## Release evidence

Each candidate should record the commit SHA, application version, generated-artifact freshness, schema migration review, known issues, rollback compatibility, and validation result. Before a provider exists, release notes are repository evidence only. Once a deployment provider exists, record staging/production URL, deployment time, health/readiness/liveness results, non-destructive smoke results, and the operator who approved promotion.

## Rollback decision

Rollback is triggered by failed health checks, a migration error, confirmed data corruption, authentication outage, critical server-error condition, or security incident. Application rollback is allowed only after checking schema compatibility; database rollback is never presumed safe. Prefer expand/contract migrations. Generated artifacts revert with the reviewed Git commit. Freeze deployment for a serious security issue until containment, repair, validation, and review are complete.

## Current release state

Validation CI is configured in the repository. Staging, deployment provider, production approval environment, domain, TLS, production PostgreSQL, backup source, and live smoke target are **blocked — external prerequisites unavailable**.
