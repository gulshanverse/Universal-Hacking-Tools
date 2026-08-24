# Knowledge Graph Governance

The knowledge graph is generated from reviewed Markdown and YAML in this repository. Its nodes are typed knowledge entities and its edges are authored metadata references, controlled prerequisite records, local lab learning mappings, and deterministic reverse edges for navigation. The committed `generated/knowledge-graph.json` is a build artifact, not an editable source of truth.

Relationship changes are made through a Git pull request that changes the relevant source metadata, passes repository validation, regenerates the graph artifacts, and receives human review. Incorrect edges are removed by correcting the reviewed source relationship and regenerating artifacts. The web application, APIs, orphan explorer, and graph suggestions have no create, update, delete, approval, or auto-link operation for canonical knowledge.

`generated/graph-health.json` reports graph version metadata, node/edge counts, orphan count, relationship coverage, prerequisite-edge count, bidirectional consistency, broken edges, unknown relationship types, and traversal limits. Its graph version is derived deterministically from the canonical ordered relationship set. A generated-contract fingerprint invalidates API graph-engine caches when source-derived artifacts change.
