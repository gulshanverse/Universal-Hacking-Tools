# Phase 10 Community Collaboration Threat Model

Phase 10 adds a **proposal and review application layer**, not an online knowledge editor. Markdown, YAML, Git history, generated contracts, pull requests, CI, and human maintainer approval remain the only route by which canonical cybersecurity knowledge can change. PostgreSQL holds untrusted draft material and collaboration state only.

| Asset | Threat | Control |
| --- | --- | --- |
| Canonical knowledge | Direct database or browser mutation | No knowledge write route, no database knowledge table, controlled proposal types, Git-only publication handoff |
| Accounts and roles | Session theft, role escalation, suspended-account bypass | Existing opaque sessions and CSRF; server-side role dependency; status check on every protected action; explicit role allowlists |
| Proposals and comments | XSS, YAML/template injection, unsafe dual-use content | Plain-text storage/rendering, HTML-free previews, bounded schemas, controlled fields, URL validation, deterministic safety findings |
| Reviews and reports | IDOR, self-review, private-report disclosure | Owner filters, reviewer/maintainer role checks, author conflict prevention, security reports private by default |
| Reputation and audits | Self-award, replay, hidden score changes | Server-created unique event keys, transparent reasons/points, append-only audit records, role separation |
| GitHub handoff | Token leakage, arbitrary paths, false success, auto-merge | Server-side provider adapter, mocked offline default, controlled type-to-path mapping, no client tokens, no auto-merge, explicit created/failed status |
| Availability and abuse | Spam, duplicate flooding, oversized input | Per-user rate limits, fixed size limits, normalized duplicate candidates, strict pagination, request-size middleware |

## Trust boundaries

> A contribution is **PROPOSED CONTENT — NOT CANONICAL KNOWLEDGE**. Validation findings are reviewer assistance, never a merge, verification, trust, or role-promotion decision.

Browsers may create bounded drafts, reports, and review comments through authenticated, CSRF-protected endpoints. The application may calculate deterministic completeness, source, relationship, safety, duplicate, and graph-impact findings. It cannot execute contributor text, create arbitrary files, run Git, write generated artifacts, or merge a pull request. A maintainer decides whether a validated proposal should be handed to the separately configured Git provider.

## Data minimization and retention

Email, session records, private learning data, security reports, internal moderation reasons, and unsubmitted drafts are not public. Public profiles expose only opt-in contributor fields and aggregate/approved contribution facts. Deleting an account removes private drafts and private state through foreign-key cascades; already published contribution attribution becomes **Former Contributor** in application views and Git history remains unchanged. Audit events retain minimal actor, action, target, reason, and timestamp for governance integrity; they are not client-deletable.

## Explicit non-goals

Phase 10 adds no direct messaging, general chat, public security disclosure thread, upload facility, arbitrary Markdown/HTML execution, remote lab, command runner, telemetry, advertising, paid ranking, token system, LLM, embedding, vector database, or automatic knowledge/verification promotion.
