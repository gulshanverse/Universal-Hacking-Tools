# Phase 9 Deterministic Graph Intelligence

The graph intelligence module extends the existing `knowledge-graph.json` through the shared `IndexLoader`. It does not parse Markdown, duplicate the parser, make network requests, or write canonical cybersecurity knowledge. Its cache is recreated when the generated-artifact fingerprint changes.

## Bounded operations

| Operation | Input boundary | Output boundary | Deterministic method |
| --- | --- | --- | --- |
| Neighborhood | depth 1–4; node limit 1–100; edge limit 1–200 | Center, nodes, edges, per-node depth, truncation flag | Breadth-first traversal ordered by relationship rank and typed ID. |
| Path | explicit start/end; maximum 25 edges | One shortest path or an empty result | Breadth-first search with stable adjacency ordering. |
| Prerequisites | one generated entity | Required, recommended, helpful, missing, completed | Existing `requires-prerequisite-*` edges plus optional owner progress. |
| Learning route | one generated entity | Ordered prerequisite route and explanations | Topological prerequisite closure; completed entities are omitted only for the authenticated owner. |
| Impact | depth 1–4 | Connected entities grouped by type | Bounded undirected neighborhood; it never models real-world impact. |
| Attack/defense | one generated entity | Techniques, vulnerabilities, detections, controls, mitigations, labs | Existing authored/generated graph edges only. |

## Ranking and explanations

Neighborhood ordering is deterministic. A candidate score is the sum of a relationship-class weight, directness weight, verification-confidence weight, and a fixed type/name tie-breaker. Direct prerequisite and mitigation edges rank before generic related edges; one-hop edges rank before farther nodes. No score changes trust metadata, validation results, or review status.

Relationship explanations use controlled templates for known relationship families such as prerequisite, mitigation, tool use, learning-path inclusion, and lab teaching. Each explanation returns a relationship type, confidence derived from the source/target verification metadata, and an evidence state. Unsupported labels return **“Explanation unavailable; relationship requires human review.”** rather than invented reasoning.

Orphan suggestions use only stable metadata overlap—category, tags, platforms, security domains, prerequisites, and learning-path references. They are labeled **SUGGESTION ONLY — REQUIRES HUMAN REVIEW** and never mutate the graph, source Markdown, or review status.
