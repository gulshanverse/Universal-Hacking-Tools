# Database Security Matrix

PostgreSQL stores only application and collaboration state. It is not a source of cybersecurity knowledge and must never receive the Markdown/YAML source corpus or generated knowledge artifacts as canonical records.

| Table group | Purpose and sensitive fields | Access and constraints | Retention / deletion intent |
| --- | --- | --- | --- |
| `users`, `user_profiles` | Normalized email, Argon2id password hash, account status, profile preferences | Private routes; unique email; application RBAC; no plaintext password | Delete with account, subject to documented published-history preservation. |
| `sessions`, verification/reset tokens | Hashed opaque session/CSRF/reset/verification tokens and expiry metadata | Server-only token comparison; expiry, revocation, and one-time-use checks | Expire or revoke; remove on account deletion. |
| learning goals, progress, bookmarks, notes, recommendations, achievements | Owner-scoped learning state and plain-text private notes | Authenticated owner scope, foreign keys, bounded inputs | Retain until owner deletion or account deletion. |
| lab attempts | Minimal safe-lab summaries and assessment results; no raw external evidence | Owner-scoped; local synthetic lab boundary | Remove on account deletion; no remote target/evidence data. |
| community profiles, contributions, versions, reviews, comments | Opt-in profile fields and controlled proposal/review workflow | Controlled templates, role gates, IDOR prevention, reviewer self-review block | Draft/private data deleted with account; published contribution history may be anonymized to preserve review provenance. |
| community reports | Private reports, including security-report classification | Owner/restricted moderation access; never public discussion | Remove or retain only as required by documented incident handling; production retention is provider-policy dependent. |
| reputation and audit events | Deterministic reputation and security-relevant workflow audit metadata | Server-side writes only; no role grants from reputation | Retention must be minimal and documented once production provider/log policy is selected. |

## Production controls required before launch

The production operator must provide PostgreSQL TLS where supported, private connectivity where supported, strong credentials, connection limits, application statement timeout, least-privilege database identities, and encrypted backup/restore evidence. The repository configures connection pooling and statement-timeout behavior for PostgreSQL but does not prove provider configuration. Separate migration, application, and backup identities are recommended where the provider supports them; actual role definitions remain **blocked — external prerequisite**.

All application access uses SQLAlchemy expressions or parameterized SQLAlchemy `text()` with no user-derived SQL construction. Migration changes follow expand/contract preference; a destructive schema operation must be explicitly reviewed, backed up, and rehearsed in an isolated environment before any production use.
