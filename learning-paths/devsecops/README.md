---
id: devsecops
type: learning-path
name: DevSecOps
status: needs-review
prerequisites:
  - networking
  - threat-modeling
concepts:
  - secure-sdlc
  - supply-chain-security
  - sbom
  - threat-modeling
tools:
  - semgrep
  - gitleaks
  - trivy
techniques:
  - security-testing
labs:
  - iac-security-review
  - secrets-rotation-exercise
technologies:
  - linux
---

# DevSecOps

> A staged, safety-first learning path.

## Goal

Build a defensible understanding of devsecops through concepts, controlled practice, evidence, detection, mitigation, and verification.

## Prerequisites

Start with the linked prerequisites and use only owned, synthetic, local, CTF, or explicitly authorized environments.

## Beginner Stage

Study the concepts first, learn the terminology, and complete the first safe lab with a written scope and cleanup plan.

## Intermediate Stage

Use the listed tools against a disposable fixture, record configuration and evidence, and explain false positives, false negatives, limitations, and defensive telemetry.

## Advanced Stage

Design a repeatable assessment or detection exercise, map findings to controls, and verify remediation without expanding beyond authorization.

## Concepts

- [Secure Sdlc](../../knowledge/concepts/secure-sdlc.md)
- [Supply Chain Security](../../knowledge/concepts/supply-chain-security.md)
- [Sbom](../../knowledge/concepts/sbom.md)
- [Threat Modeling](../../knowledge/concepts/threat-modeling.md)

## Techniques

- [Security Testing](../../knowledge/techniques/security-testing.md)

## Tools

- [Semgrep](../../tools/secure-development/semgrep.md)
- [Gitleaks](../../tools/secure-development/gitleaks.md)
- [Trivy](../../tools/vulnerability-management/trivy.md)

## Vulnerabilities

Use the [vulnerability encyclopedia](../../vulnerabilities/README.md) to choose implementation-specific classes rather than assuming a finding.

## Labs

- Iac Security Review
- Secrets Rotation Exercise

## Defensive Knowledge

Connect each exercise to logging, least privilege, secure configuration, segmentation, and remediation verification.

## Suggested Projects

Create a small, disposable project that documents scope, assumptions, evidence, limitations, controls, cleanup, and completion criteria. Never publish secrets, personal data, malicious payloads, or results from uninvolved systems.

## Completion Criteria

You can explain the concepts, select an authorized method, preserve evidence, communicate uncertainty, recommend mitigation, and verify a fix.
