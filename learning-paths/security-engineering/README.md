# Security Engineering

> A staged, safety-first learning path.

## Prerequisites

A basic understanding of computers, permission to use the lab environments, and a commitment to authorized testing only.

## Topics

1. Threat modeling
2. Secure design
3. Secure coding
4. Dependency and IaC risk
5. Security testing in CI
6. Operational controls

## Tools

* [Semgrep](../../tools/secure-development/semgrep.md)
* [Bandit](../../tools/secure-development/bandit.md)
* [Checkov](../../tools/secure-development/checkov.md)
* [OSV-Scanner](../../tools/secure-development/osv-scanner.md)

## Labs

* Container Image SBOM and Scan
* Detection Rule Engineering

## Projects

Build a small, disposable project that documents scope, assumptions, evidence, defensive interpretation, remediation, and cleanup. Do not publish secrets, personal data, malicious payloads, or results from uninvolved systems.

## Recommended Progression

Read the concepts first, complete the beginner lab, repeat with a documented hypothesis, then write a short report and defensive test. Move forward only when you can explain limitations and legal boundaries.

## Expected Skills

You should be able to explain the underlying concept, select an appropriate authorized tool, preserve evidence, communicate uncertainty, recommend mitigation, and verify a fix.

## Goal

Build a defensible understanding of security engineering through concepts, controlled practice, evidence, detection, mitigation, and remediation verification.


## Beginner Stage

Study the terminology and foundational concepts, define authorization and scope, and complete a local or synthetic lab before using assessment tooling.


## Intermediate Stage

Apply the concepts to a disposable fixture, preserve evidence and assumptions, explain limitations, and map observations to defensive controls.


## Advanced Stage

Design a repeatable authorized assessment or detection exercise, compare alternative controls, and verify remediation without expanding scope.


## Concepts

Start with the concepts linked from the knowledge taxonomy and confirm the relevant trust boundaries before selecting tools.


## Vulnerabilities

Use the [vulnerability encyclopedia](../../vulnerabilities/README.md) to study root causes and mitigations; do not assume that a category name proves a finding.


## Defensive Knowledge

Connect every exercise to ownership, logging, least privilege, secure configuration, segmentation, response, and remediation verification.


## Suggested Projects

Create a small disposable project that documents scope, assumptions, evidence, uncertainty, controls, cleanup, and completion criteria. Never publish secrets or personal data.


## Completion Criteria

You can explain the concepts, choose an authorized method, preserve evidence, communicate uncertainty, recommend mitigation, and verify a fix.


## Related Knowledge

- [Networking](../../knowledge/concepts/networking.md)
- [Security Testing](../../knowledge/techniques/security-testing.md)
- [Secure Configuration](../../knowledge/defensive-controls/secure-configuration.md)
