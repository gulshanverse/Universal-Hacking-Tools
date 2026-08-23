---
id: evidence-first-analysis
type: lab
name: Evidence-First Analysis Workflow
status: unverified
verification:
  status: unverified
  confidence: unknown
  last_verified:
  verification_method: manual-review
  reviewer: repository-audit
  review_notes: Legacy page standardized in Phase 5; claims require future evidence-level review.
sources:
  - https://github.com/gulshanverse/Universal-Hacking-Tools

---

# Evidence-First Analysis Workflow

> Controlled, authorized lab exercise.

## Objective

Practice hashing, chain-of-custody notes, timeline reasoning, and a concise forensic report.

## Difficulty

Intermediate

## Prerequisites

Basic security concepts, a disposable lab, and permission to use every system, account, sample, and dataset involved.

## Environment

Synthetic disk image or provided training artifact; Autopsy. Keep the environment isolated from production and unrelated networks.

## Setup

Read the upstream documentation for the selected tools, create only synthetic or intentionally vulnerable fixtures, take a snapshot, and document the scope and cleanup plan.

## Learning Goals

* Explain the security concept in your own words.
* Record inputs, observations, uncertainty, and evidence provenance.
* Connect the observation to a defensive control and a verification test.

## Tasks

1. Define the lab boundary and expected result.
2. Perform the smallest safe action that answers the objective.
3. Capture relevant output without collecting unrelated personal or production data.
4. Write a short finding with evidence, limitation, and remediation.

## Expected Observations

Results should be reproducible within the lab and should include timestamps, tool configuration, and the known fixture state. An unexpected result is a prompt to inspect assumptions, not permission to expand scope.

## Defensive Interpretation

Map the observation to relevant logs, detections, hardening measures, and ownership. Explain what a defender could see and what would reduce exposure.

## Cleanup

Stop services, delete temporary credentials and artifacts, revert snapshots, remove test data, and confirm that no secrets or personal data remain in the repository or logs.

## Further Learning

Read the linked tool pages, the relevant OWASP or NIST guidance, and the upstream documentation. Repeat the exercise with a changed fixture and explain why the result differs.

## Related Knowledge

- [Networking](../../knowledge/concepts/networking.md)
- [Security Monitoring](../../knowledge/concepts/security-monitoring.md)
- [Network Scanning](../../knowledge/techniques/network-scanning.md)
- [Packet Analysis](../../knowledge/techniques/packet-analysis.md)
- [Secure Logging](../../knowledge/defensive-controls/secure-logging.md)
