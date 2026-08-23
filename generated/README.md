# Generated Knowledge Artifacts

The JSON files in this directory are generated from Markdown, YAML, and the selective evidence ledger. Do not edit them manually.

Run:

```bash
python3 scripts/generate-knowledge.py
python3 scripts/generate-search.py
python3 scripts/generate-quality-reports.py
python3 scripts/generate-trust-reports.py
python3 scripts/validate-knowledge.py
python3 scripts/validate-quality.py
python3 scripts/validate-trust.py
python3 scripts/validate-schemas.py
python3 scripts/generate-index.py --check
python3 scripts/generate-knowledge.py --check
python3 scripts/generate-search.py --check
python3 scripts/generate-quality-reports.py --check
python3 scripts/generate-trust-reports.py --check
```

The Phase 1–4 artifacts include typed indexes for tools, vulnerabilities, concepts, techniques, technologies, defensive controls, labs, and learning paths; `knowledge-graph.json` with deterministic nodes and bidirectional relationships; `search-index.json` with normalized searchable documents; `aliases.json` with legitimate terminology mappings; `knowledge-health.json` with content-health metrics; `content-completeness.json` with per-entity gaps; `verification-report.json` with status, confidence, category, source, claim, and relationship findings; and `review-queue.json` with deterministic remediation priorities.

Phase 5 adds `source-catalog.json` with normalized source records and non-destructive duplicate findings; `claim-report.json` with the selective evidence-backed claim ledger and traceability findings; `prerequisite-report.json` with required, recommended, helpful, duplicate, and cycle findings; and `trust-report.json` with transparent entity, source, claim, relationship, prerequisite, and overall trust summaries.

Generated artifacts are deterministic. They use the controlled `--as-of` and stale-age inputs where time-dependent reporting is needed, and they do not perform live internet monitoring, execute repository content, or introduce a database, frontend, external search service, or LLM.
