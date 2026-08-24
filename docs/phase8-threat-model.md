# Phase 8 Threat Model

Phase 8 introduces private application state while preserving the Git repository and generated contracts as the only authoritative cybersecurity knowledge source. The model applies to the FastAPI application-state layer, PostgreSQL, browser cookie session, local safe-lab integration, and Next.js dashboard. It does not authorize remote lab execution, public profiles, community features, telemetry, or editing repository content.

| Threat | Impact | Likelihood | Mitigation | Residual risk |
| --- | --- | --- | --- | --- |
| Account takeover or credential stuffing | Unauthorized private-state access | Medium | Argon2id hashes, generic auth responses, scoped in-process rate limits, session rotation, logout-all | Distributed attacks require shared production rate limiting in a later deployment phase |
| Session theft or fixation | Account impersonation | Medium | Random opaque server-side tokens, token hash storage, HttpOnly/SameSite cookies, rotation after login, revocation and expiry | A compromised browser or trusted same-origin script can still act as its user |
| Email verification or reset abuse | Unauthorized activation or password reset | Medium | Single-use, hashed, short-lived random tokens; generic reset request; injectable email interface; no token logs | Delivery-channel compromise is outside application control |
| Authorization bypass or IDOR | Cross-user note, progress, bookmark, goal, or attempt disclosure | High | Derive ownership exclusively from authenticated session; scoped repository queries; deliberate 404 responses; multi-user tests | Application regressions require continued code review and authorization tests |
| Privilege escalation | Unauthorized maintenance access | Low | No public admin surface or role-escalation endpoint in Phase 8 | Future admin features require a separate model and review |
| SQL injection | Database compromise | Medium | SQLAlchemy bound parameters and modeled queries; no interpolated SQL; input validation tests | ORM misuse remains possible and is scanned in review |
| Stored XSS through notes | Session misuse or deceptive UI | Medium | Plain-text notes only, 20,000-character limit, no raw HTML rendering, React escaping | URLs in plain text can still be socially deceptive |
| CSRF | Unwanted authenticated state change | Medium | SameSite cookie plus double-submit CSRF token for unsafe cookie-auth requests; origin checks | Browser policy differences and same-origin XSS remain residual risks |
| Token or secret leakage | Session/reset/verification compromise | Medium | Hash stored tokens, redacted structured logs, environment-only secrets, safe response models | Operators must protect environment variables and backups |
| Sensitive-data exposure | Private learning data disclosure | Medium | Data minimization, private routes, no email in URLs, minimal lab summary retention, deletion workflow | Database compromise may expose retained account state |
| Lab evidence leakage | Disclosure of educational artifacts | Medium | Persist only attempt status, score, and task completion; keep raw Phase 6 evidence ephemeral | A learner can still record their own local fixture observations elsewhere |
| Cross-user progress access | Privacy breach | High | Session-scoped queries, unique ownership constraints, negative authorization tests | Bugs require regression tests and security review |
| Database compromise | Broad account-state disclosure | Low | Least-privilege DB credentials, encrypted transport in production, backups documented but not provisioned | Backup and infrastructure controls remain a production responsibility |
| Enumeration | Confirmation that an email exists | Medium | Generic register, login, verification, and reset messages; rate limits | Timing and delivery side channels are reduced, not eliminated |
| Rate-limit bypass | Brute-force or endpoint abuse | Medium | Per-client in-process limits and bounded requests; documented shared-store requirement for multi-instance production | In-process limits do not coordinate across instances |
| Recommendation abuse | Resource exhaustion or misleading plan output | Low | Authenticated access, bounded filters/results, deterministic artifact-only computation | High-volume production abuse requires shared rate limiting |
| Malicious notes or content | UI abuse or oversized data | Medium | Plain-text storage, strict request and note limits, no HTML/Markdown execution | Text content can still be misleading to its owner |

## Security invariants

The API never accepts a client-provided `user_id` as an ownership authority. Public knowledge endpoints remain read-only and work when PostgreSQL is unavailable; authenticated state-changing routes return a clear degraded-state response instead of buffering or silently losing writes. Phase 8 retains local, synthetic, authorized lab execution and records only minimal educational summaries after an assessment.

## Review triggers

Any future addition of social features, user-uploaded files, public profiles, durable lab artifacts, remote execution, third-party analytics, a shared rate-limit service, database replicas, or administrative capabilities requires a revision of this threat model before implementation.
