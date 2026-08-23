# Authorized Interactive Labs

Phase 6 adds a **local-first, disposable, deterministic lab framework** around a small reference set of existing lab pages. The CLI reads committed definitions and synthetic fixtures only. It does not expose a shell, contact external systems, pull targets or images, use a database, or execute arbitrary commands from YAML.

## Inventory

The 22 existing labs are classified in their Markdown front matter as `documentation-only`, `guided`, or `executable`. Only six are executable in Phase 6: DNS Resolution and Inventory, TLS Certificate Review, API Discovery in a Local App, Detection Rule Regression, IaC Security Review, and Kubernetes Posture Review. The remaining labs remain documentation-first or guided until they receive separate review and a safe definition.

## Quick start

```bash
python3 scripts/lab.py list
python3 scripts/lab.py validate
python3 scripts/lab.py --format json create dns-resolution-inventory --dry-run
python3 scripts/lab.py --state-root /tmp/uht-labs create dns-resolution-inventory
```

The `create` command prints a local instance identifier. Use it with `start`, `status`, `run`, `evidence`, `assess`, `stop`, `reset`, and `destroy`. Runtime state lives under the selected temporary state root and is not part of the repository.

## Source of truth

Each executable definition is a JSON-compatible YAML file under [`labs/definitions/`](definitions/). JSON is used as a dependency-free YAML 1.2 subset so the project can validate definitions with the Python standard library only. Synthetic fixture data is under [`labs/fixtures/`](fixtures/), and the schema is [`labs/schemas/lab.schema.json`](schemas/lab.schema.json).

Read the design and authoring documentation before creating a new executable lab:

- [`docs/lab-architecture.md`](../docs/lab-architecture.md)
- [`docs/lab-safety.md`](../docs/lab-safety.md)
- [`docs/lab-authoring-guide.md`](../docs/lab-authoring-guide.md)
- [`docs/lab-assessment.md`](../docs/lab-assessment.md)
- [`docs/lab-threat-model.md`](../docs/lab-threat-model.md)

The lab linter is [`scripts/validate-labs.py`](../scripts/validate-labs.py). Generated catalog, health, and report artifacts are written to `generated/lab-catalog.json`, `generated/lab-health.json`, and `generated/lab-report.json`.
