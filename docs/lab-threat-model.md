# Phase 6 Lab Threat Model

The lab engine is designed for educational use on a trusted local checkout. Its primary security objective is to ensure that a lab definition cannot turn the repository’s CLI into an unrestricted host or network execution mechanism.

| Threat | Phase 6 mitigation |
|---|---|
| Malicious or malformed definition | Schema and safety linter; closed fields; unknown actions rejected |
| Arbitrary command execution | No shell field, no subprocess runner, no `eval` or `exec`, closed action registry |
| Network escape | Reference runner reads local files only; safety requires no internet and no host networking |
| Host filesystem access | Fixture paths are relative, traversal is rejected, no host mounts are accepted |
| Privileged execution | Definitions require `privileged: false`; no container adapter is enabled |
| Resource exhaustion | CPU, memory, PID, timeout, and one-instance bounds are required |
| Secret exposure | Fixtures and evidence are screened for common secret-like patterns; runtime state is ephemeral |
| Evidence leakage | Evidence is stored below a caller-selected temporary state root and cleared on reset/destroy |
| Persistent state leakage | Destroy removes manifest, audit, and evidence files, retaining only a minimal tombstone |
| Unsafe content correctness | Execution status is separate from Phase 5 verification and trust status; human review remains required |

The threat model does not claim to provide a hardened multi-tenant sandbox. That would require a separately reviewed isolation adapter and platform architecture. Phase 6 therefore limits execution to committed synthetic JSON fixtures and keeps container, cloud, remote-target, and arbitrary process capabilities out of scope.

## Review requirements

Contributors must inspect the complete definition and fixture, run negative safety tests, confirm that the Markdown page describes the same local scope, and obtain security review before merging an executable lab. A passing automated linter is necessary but not sufficient evidence that a lab is safe or educationally correct.
