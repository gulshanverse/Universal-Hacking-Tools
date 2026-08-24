# Production Threat Model

> **Status vocabulary:** `not-configured` means no repository evidence of a configured resource; `configured` means repository configuration exists but has not been exercised in the target environment; `validated` means an automated local or CI control has passed; `verified` requires recorded evidence from the relevant target environment; `blocked` requires an external prerequisite.

This threat model covers the Phase 11 production posture of Universal Hacking Tools. It does not assert that the application is publicly deployed. Git-backed Markdown/YAML and deterministic generated JSON remain the only cybersecurity knowledge authority. PostgreSQL remains limited to private application and collaboration state.

## Current boundary and status

| Component | Intended role | Current evidence status | Production implication |
| --- | --- | --- | --- |
| Git repository and generated artifacts | Canonical cybersecurity knowledge and deterministic read contracts | `validated` in repository CI before Phase 11 | Canonical changes require reviewed Git changes and artifact freshness checks. |
| FastAPI service | Public read API and private application-state boundary | `configured` | Requires production environment validation, explicit origins, secrets, HTTPS termination, and deployment evidence. |
| Next.js web client | Public knowledge archive and role-bound private/community interface | `configured` | Requires production build configuration, public-origin review, and platform header/TLS evidence. |
| PostgreSQL | Accounts, sessions, learning references, community workflow, audit records | `blocked` | No production PostgreSQL provider, private connectivity, credentials, backup, or restore evidence is configured in this repository. |
| Local safe labs | Synthetic, bounded, local-fixture lifecycle only | `validated` in repository tests | Must not become a remotely executable production service. |
| Git provider adapter | Optional, server-only handoff boundary | `configured` with unavailable default | No production credential or provider is configured; manual pull-request fallback remains required. |
| Domain, DNS, TLS, edge/WAF, monitoring, backups | External deployment infrastructure | `blocked` | No domain, certificate, provider, monitoring, or backup resource is evidenced here. |

## Internet-facing threats

| Threat | Existing control | Phase 11 production control | Status |
| --- | --- | --- | --- |
| Credential attacks and account enumeration | Argon2id hashing, password policy, generic authentication responses, opaque sessions | Production secret validation, explicit rate-limit policy, HTTPS-only secure cookies, and operational alerting | `configured` pending target-environment verification |
| Session theft and CSRF | HttpOnly session cookie, double-submit CSRF token, origin allowlist | Secure-cookie enforcement, explicit production origin allowlist, secret rotation runbook, and HTTPS verification | `configured` pending TLS and deployment evidence |
| XSS, malicious Markdown, and executable SVG | Plain-text community validation and no arbitrary HTML rendering | CSP/header verification and browser production audit | `configured` pending deployment header evidence |
| SQL injection and IDOR | SQLAlchemy queries, owner scoping, RBAC, CSRF-protected mutations | Route-security matrix, production regression tests, and database least privilege | `validated` in existing test suite; database-role separation `blocked` |
| API spam and graph/search exhaustion | Bounded graph/search/pagination routes and local limiters | Explicit endpoint policy; edge or shared rate limiting for multi-instance deployment | `configured`; multi-instance enforcement `blocked` until provider architecture is chosen |
| Community abuse and private-report leakage | Controlled templates, privacy boundaries, self-review prevention, moderation/audit records | Production review queue, abuse response, and privacy-safe logs | `validated` in Phase 10 tests; operations `blocked` without production service |
| Lab abuse | Fixed local synthetic fixtures and closed lifecycle | Keep remote execution disabled; validate ownership, expiry, reset, destroy, and evidence bounds | `validated` in existing tests |
| Git-provider abuse | Server-only unavailable/mock adapter and no automatic merge | Optional least-privilege server credential, PR-only workflow, audit, and manual fallback | `blocked` for a real provider; safe default `validated` |

## Infrastructure threats

| Threat | Required treatment | Current status |
| --- | --- | --- |
| Secret leakage | Server-only storage, startup rejection of unsafe production configuration, redacted structured logs, rotation/revocation procedures | `configured` baseline; target secret store `blocked` |
| Compromised deployment or supply chain | Least-privilege CI, locked dependencies, reviewed deployment context, reproducible build and commit identity | `configured` repository baseline; deployment environment `blocked` |
| Database compromise or exposure | Private network where available, TLS where supported, least-privilege roles, connection/timeouts, encrypted backups, restore runbook | `blocked` pending production PostgreSQL/provider design |
| Log or backup exposure | Data minimization, no secret/payload logging, access controls, retention, encryption, and restore evidence | `not-configured` until a provider/log sink/backup service exists |
| CORS, host, or internal-service exposure | Explicit public origins, trusted host policy, no wildcard credentialed CORS, non-public database/lab services | `configured` in code baseline; externally verified state `blocked` |
| Container escape | No container runtime is defined in the repository; do not infer container isolation | `not-configured` |

## Operational threats

| Threat | Required response | Current status |
| --- | --- | --- |
| Database outage | Keep generated public knowledge available; fail private routes closed without traces | `validated` in existing tests |
| Bad deployment or migration failure | Backup, migration rehearsal, health gate, smoke tests, safe rollback decision | `configured` as repository runbook work; target execution `blocked` |
| Corrupt or missing generated artifact | Fail safely rather than serving inconsistent knowledge; run artifact freshness gates | `validated` in repository controls |
| Backup/restore failure | Isolated restore drill, documented RPO/RTO only after provider selection | `blocked` |
| Certificate, DNS, or provider outage | Provider runbook, health monitoring, controlled incident response | `blocked` |

## Non-goals and invariants

Phase 11 does not add AI, embeddings, vector storage, public security reports, remote attack execution, remote labs, arbitrary commands, arbitrary uploads, public repository editing, autonomous GitHub actions, telemetry-based behavioral surveillance, or a new canonical knowledge store. Production hardening must preserve the existing public-read/private-fail-closed boundary and must never convert a proposed community record into canonical cybersecurity knowledge.
