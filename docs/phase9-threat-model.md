# Phase 9 Graph Intelligence Threat Model

Phase 9 makes the existing generated knowledge graph easier to traverse and explain. It does not change the knowledge-authority model: Markdown and YAML are reviewed in Git, deterministic generators produce committed JSON artifacts, and graph intelligence reads those artifacts only. PostgreSQL remains limited to Phase 8 private state and may be consulted only to overlay the authenticated caller's progress and selected learning goals.

| Asset or boundary | Threat | Required control |
| --- | --- | --- |
| Generated graph | Traversal or response-size exhaustion | Reject depth above 4, nodes above 100, edges above 200, and paths above 25 before traversal; set endpoint-specific rate limits. |
| Knowledge integrity | Invented or web-authored relationship | Use only generated relationships; mark heuristic orphan suggestions as human-review-only; expose no knowledge mutation route. |
| Private learning state | Cross-user progress leakage | Resolve the optional principal from the server-side session and query only its owner-scoped rows; never accept a user ID parameter. |
| Public caching | Personalized response shared publicly | Keep public graph outputs artifact-keyed and keep progress overlays uncached/private. |
| Graph renderer | XSS or SVG injection | Render API strings as React text, never accept SVG/HTML markup, and do not construct dynamic scriptable attributes. |
| Exports | Sensitive state leakage | Export public node/edge data; authenticated exports may add only caller-owned progress labels and omit emails, notes, tokens, identifiers, and lab evidence. |
| Relationship explanations | Fabricated rationale | Explain only relationship labels with controlled templates; otherwise return an explicit human-review-needed state. |

> Graph intelligence describes relationships in the repository knowledge system. It is not a scanner, target selector, infrastructure-impact engine, remote lab trigger, or authorization for real-world activity.

All graph endpoints return stable sanitized errors and are read-only. Inputs are explicit IDs, filters, and bounded integers; no natural-language command interpreter, LLM, embedding, vector store, remote data source, or generic execution surface is introduced.
