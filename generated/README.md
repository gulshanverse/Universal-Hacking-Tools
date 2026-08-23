# Generated Knowledge Artifacts

The JSON files in this directory are generated from Markdown and YAML source metadata. Do not edit them manually.

Run:

```bash
python3 scripts/generate-knowledge.py
python3 scripts/generate-search.py
python3 scripts/generate-quality-reports.py
python3 scripts/validate-knowledge.py
python3 scripts/validate-quality.py
python3 scripts/validate-schemas.py
python3 scripts/generate-index.py --check
python3 scripts/generate-knowledge.py --check
python3 scripts/generate-search.py --check
python3 scripts/generate-quality-reports.py --check
```

The artifacts include typed indexes for tools, vulnerabilities, concepts, techniques, technologies, defensive controls, labs, and learning paths; `knowledge-graph.json` containing deterministic nodes and bidirectional relationships; `search-index.json` containing normalized searchable documents; `aliases.json` containing legitimate terminology mappings; `knowledge-health.json` containing deterministic content-health metrics; `content-completeness.json` containing per-entity section, metadata, source, relationship, and verification gaps; `verification-report.json` containing totals by entity type; and `review-queue.json` containing a transparent priority queue for human remediation. They are intended to support a future search or web frontend without introducing a database in this phase.
