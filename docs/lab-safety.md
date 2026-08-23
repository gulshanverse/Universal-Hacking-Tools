# Phase 6 Lab Safety

Every executable lab is restricted to a **local synthetic fixture** and must declare `authorized_only: true`, `internet_access: false`, and `isolation_required: true`. The current implementation has no network-capable runner and does not provide a mechanism for weakening these constraints.

## Required invariants

| Boundary | Required value |
|---|---|
| Scope | `local-synthetic-fixture` |
| Environment | `local-fixture` with `dedicated-ephemeral` isolation |
| Network policy | `isolated-no-internet` |
| Host networking | `false` |
| Privileged execution | `false` |
| Host mounts | `false` |
| Maximum instances | `1` per lab |
| Execution timeout | 1–600 seconds; reference labs use 180 seconds |
| Memory | Bounded megabyte value; reference labs use 256 MB |
| Process IDs | 16–256; reference labs use 64 |

The linter rejects missing or unsafe declarations, unknown actions, invalid fixture paths, unbounded resources, unsupported target types, and unresolved learning references. It also checks fixtures for obvious secret-like patterns.

## Host protection

The runner performs read-only inspection of committed fixture JSON. It does not accept shell strings, arbitrary commands, user-provided host paths, privileged settings, host networking, credential paths, cloud metadata, or environment-secret access. The allowlist is intentionally small: fixture inspection actions for DNS, TLS metadata, HTTP response maps, logs, IaC manifests, and container posture.

## Fixtures

Fixtures are synthetic, local, disposable, and intentionally bounded. They contain no real credentials, personal data, malware, persistence, destructive payloads, production secrets, cloud account access, or real-world targets. A fixture is educational input, not a deployment target.

## Future container adapters

Docker-backed execution is not enabled by this phase. Any future adapter must be separately reviewed and must preserve no-internet networking, no host networking, no privileged mode, no arbitrary host mounts, bounded CPU/memory/PIDs/time, dropped capabilities, and disposable cleanup. A definition must never silently relax a safety invariant.
