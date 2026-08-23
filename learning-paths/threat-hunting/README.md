---
id: threat-hunting
type: learning-path
name: Threat Hunting
status: needs-review
prerequisites:
  - networking
  - threat-modeling
concepts:
  - security-monitoring
  - threat-modeling
  - processes
  - memory
tools:
  - wazuh
  - osquery
  - velociraptor
techniques:
  - security-testing
labs:
  - detection-rule-regression
  - memory-image-triage
technologies:
  - linux
verification:
  status: needs-review
  confidence: low
  last_verified:
  verification_method: manual-review
  reviewer: repository-audit
  review_notes: Phase 5 metadata audit only; factual claims remain pending claim-level evidence.

sources:
  - https://github.com/gulshanverse/Universal-Hacking-Tools

---

# Threat Hunting

> A staged, safety-first learning path.

## Goal

Build a defensible understanding of threat hunting through concepts, controlled practice, evidence, detection, mitigation, and verification.

## Prerequisites

Start with the linked prerequisites and use only owned, synthetic, local, CTF, or explicitly authorized environments.

## Beginner Stage

Study the concepts first, learn the terminology, and complete the first safe lab with a written scope and cleanup plan.

## Intermediate Stage

Use the listed tools against a disposable fixture, record configuration and evidence, and explain false positives, false negatives, limitations, and defensive telemetry.

## Advanced Stage

Design a repeatable assessment or detection exercise, map findings to controls, and verify remediation without expanding beyond authorization.

## Concepts

- [Security Monitoring](../../knowledge/concepts/security-monitoring.md)
- [Threat Modeling](../../knowledge/concepts/threat-modeling.md)
- [Processes](../../knowledge/concepts/processes.md)
- [Memory](../../knowledge/concepts/memory.md)

## Techniques

- [Security Testing](../../knowledge/techniques/security-testing.md)

## Tools

- [Wazuh](../../tools/defensive-security/wazuh.md)
- [Osquery](../../tools/defensive-security/osquery.md)
- [Velociraptor](../../tools/defensive-security/velociraptor.md)

## Vulnerabilities

Use the [vulnerability encyclopedia](../../vulnerabilities/README.md) to choose implementation-specific classes rather than assuming a finding.

## Labs

- Detection Rule Regression
- Memory Image Triage

## Defensive Knowledge

Connect each exercise to logging, least privilege, secure configuration, segmentation, and remediation verification.

## Suggested Projects

Create a small, disposable project that documents scope, assumptions, evidence, limitations, controls, cleanup, and completion criteria. Never publish secrets, personal data, malicious payloads, or results from uninvolved systems.

## Completion Criteria

You can explain the concepts, select an authorized method, preserve evidence, communicate uncertainty, recommend mitigation, and verify a fix.
