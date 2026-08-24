# Phase 9 Graph API

All graph API routes are read-only generated-knowledge routes under `/api/v1`. They preserve the Phase 7 public API and are rate limited. The graph version is the generated artifact fingerprint; `generated_at` identifies the controlled repository artifact date rather than live data.

| Route | Access | Purpose |
| --- | --- | --- |
| `GET /graph/neighborhood` | Public; optional private overlay | Bounded neighborhood around one entity with type, relationship, and trust filters. |
| `GET /graph/path` | Public | Deterministic shortest path between two generated entities. |
| `GET /graph/impact` | Public | Bounded repository-knowledge connectivity grouped by entity type. |
| `GET /graph/prerequisites` | Public; optional private overlay | Prerequisite groups and caller-owned completion state. |
| `GET /graph/attack-defense` | Public | Existing authored attack/defense-related connections. |
| `GET /knowledge/{id}/prerequisites` | Public; optional private overlay | Entity-context alias for prerequisite analysis. |
| `GET /knowledge/{id}/learning-route` | Public; optional private overlay | Deterministic prerequisite route. |
| `GET /knowledge/{id}/impact` | Public | Entity-context impact analysis. |
| `GET /knowledge/{id}/attack-defense` | Public | Entity-context attack/defense analysis. |
| `GET /discover` | Public | Explicit typed discovery rather than natural-language interpretation. |
| `GET /me/knowledge-gaps` | Authenticated | Caller-owned deterministic gap analysis. |

Every traversal rejects out-of-range parameters instead of clamping untrusted values. Public exports include only graph version metadata and public nodes/relationships. Authenticated overlays and exports contain no email, session, database ID, note, or lab-evidence data.
