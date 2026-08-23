# Generated Knowledge Artifacts

The JSON files in this directory are generated from Markdown and YAML source metadata. Do not edit them manually.

Run:

```bash
python3 scripts/generate-knowledge.py
python3 scripts/validate-knowledge.py
python3 scripts/generate-knowledge.py --check
```

The artifacts include typed indexes for tools, vulnerabilities, concepts, techniques, technologies, defensive controls, labs, and learning paths, plus `knowledge-graph.json` containing deterministic nodes and bidirectional relationships. They are intended to support a future search or web frontend without introducing a database in this phase.
