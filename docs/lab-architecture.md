# Phase 6 Lab Architecture

Phase 6 treats an executable lab as a **declarative local-fixture exercise**, not as a general-purpose remote execution service. Existing Markdown pages remain the learner-facing source of context and safety boundaries. A small definition file adds machine-readable targets, tasks, evidence, assessment criteria, cleanup, and learning mappings.

## Components

| Component | Location | Responsibility |
|---|---|---|
| Lab page | `labs/**/*.md` | Objective, explanation, safety framing, and classification |
| Definition | `labs/definitions/*.yaml` | JSON-compatible YAML contract for executable metadata |
| Fixture | `labs/fixtures/**/*.json` | Committed synthetic input; no credentials or personal data |
| Schema and linter | `labs/schemas/`, `scripts/validate-labs.py` | Structural and safety validation |
| Lifecycle | `labs/engine/lifecycle/manager.py` | Filesystem-backed disposable instance state |
| Runner | `labs/runners/local_fixture.py` | Closed action registry over committed fixture files |
| Evidence | `labs/engine/evidence/store.py` | Ephemeral, secret-screened JSON records |
| Assessment | `labs/engine/assessment/engine.py` | Deterministic rubric evaluation |
| Reports | `scripts/generate-lab-reports.py` | Catalog, health, and report artifacts |
| CLI | `scripts/lab.py` | Local interface for lifecycle and assessment commands |

## Lifecycle

The manager implements `create → start → run → assess → stop → reset/destroy`. Each state transition is explicit and invalid transitions are rejected. A created instance is assigned a local identifier and receives a manifest containing only the lab definition, safety settings, bounded resources, target references, and allowed actions.

`reset` clears ephemeral evidence and returns the instance to a clean ready state. `destroy` clears evidence, removes the manifest and audit stream, and retains only a minimal destroyed-state tombstone so later attempts to start the instance are rejected. Runtime timestamps are permitted in temporary state; committed reports use the fixed Phase 6 reporting date.

## Execution boundary

The reference runner reads a committed JSON fixture and invokes only a named action from the definition’s allowlist. It does not parse or execute shell strings, invoke `subprocess`, contact a network, start containers, mount host paths, or access credentials. Docker support is intentionally deferred until a separately reviewed adapter can prove the same isolation and resource invariants.

## Integration boundary

Executable definitions map to existing graph entities through `teaches-concept`, `practices-technique`, `uses-tool`, `demonstrates-vulnerability`, `reinforces-control`, and `belongs-to-learning-path` edges. Execution correctness and content correctness remain separate: a successful local fixture run never upgrades verification status.
