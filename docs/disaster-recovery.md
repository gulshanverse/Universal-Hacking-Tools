# Disaster Recovery and Backup Boundary

## Current status

| Capability | Status | Evidence | Required action |
| --- | --- | --- | --- |
| Production database backup | `blocked` | No production database provider or backup resource is configured. | Select provider, encryption/access policy, frequency, retention, and backup owner. |
| Isolated restore drill | `blocked` | No production backup source exists. | Restore a backup into an isolated database, run migration preflight, start the application, and verify critical public/private flows. |
| Deployment recovery | `not-configured` | No public hosting provider is specified. | Select provider and document safe application rollback. |
| Git knowledge recovery | `configured` | Canonical knowledge remains versioned in Git. | Use reviewed Git rollback/revert procedures; regenerate and validate artifacts. |
| Manual Git handoff fallback | `configured` | Provider remains unavailable by default. | Use normal reviewed repository pull requests. |

## Required backup and restore process

The deployment operator must define daily-or-better backup frequency, encryption at rest and in transit, retention, access control, owner, and deletion-from-backup behavior. RPO and RTO remain **TBD — infrastructure prerequisite** until a provider and observed restore data exist. Do not infer immediate physical deletion from immutable backups; document the provider’s retention/expiration behavior.

The isolated restore drill must follow this sequence: select a verified backup; restore it into a non-production database; use a separately scoped database URL; run `make migration-preflight`; start the API with non-production configuration; verify generated public knowledge, private authentication, owner isolation, community privacy, and health endpoints; record start/end, source age, migration result, critical-flow result, and duration. Never restore a backup over a production database as a test.

## Outage and recovery priorities

For database outage, keep generated public knowledge available and fail private features closed. For GitHub outage, preserve the manual PR process and do not describe a handoff as successful. For DNS, TLS, or hosting failure, use the selected provider’s status and change-control process once one exists. For secret or database compromise, follow [incident response](incident-response.md) before resuming deployment.
