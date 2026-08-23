---
id: api-security
type: learning-path
name: API Security
status: needs-review
prerequisites:
  - networking
  - threat-modeling
concepts:
  - apis
  - rest
  - graphql
  - authentication
  - authorization
tools:
  - httpie
  - owasp-zap
  - nuclei
techniques:
  - security-testing
labs:
  - api-discovery-local-app
  - graphql-schema-safety
technologies:
  - linux
---

# API Security

> A staged, safety-first learning path.

## Goal

Build a defensible understanding of api security through concepts, controlled practice, evidence, detection, mitigation, and verification.

## Prerequisites

Start with the linked prerequisites and use only owned, synthetic, local, CTF, or explicitly authorized environments.

## Beginner Stage

Study the concepts first, learn the terminology, and complete the first safe lab with a written scope and cleanup plan.

## Intermediate Stage

Use the listed tools against a disposable fixture, record configuration and evidence, and explain false positives, false negatives, limitations, and defensive telemetry.

## Advanced Stage

Design a repeatable assessment or detection exercise, map findings to controls, and verify remediation without expanding beyond authorization.

## Concepts

- [Apis](../../knowledge/concepts/apis.md)
- [Rest](../../knowledge/concepts/rest.md)
- [Graphql](../../knowledge/concepts/graphql.md)
- [Authentication](../../knowledge/concepts/authentication.md)
- [Authorization](../../knowledge/concepts/authorization.md)

## Techniques

- [Security Testing](../../knowledge/techniques/security-testing.md)

## Tools

- [Httpie](../../tools/web-security/httpie.md)
- [Owasp Zap](../../tools/web-security/owasp-zap.md)
- [Nuclei](../../tools/web-security/nuclei.md)

## Vulnerabilities

Use the [vulnerability encyclopedia](../../vulnerabilities/README.md) to choose implementation-specific classes rather than assuming a finding.

## Labs

- Api Discovery Local App
- Graphql Schema Safety

## Defensive Knowledge

Connect each exercise to logging, least privilege, secure configuration, segmentation, and remediation verification.

## Suggested Projects

Create a small, disposable project that documents scope, assumptions, evidence, limitations, controls, cleanup, and completion criteria. Never publish secrets, personal data, malicious payloads, or results from uninvolved systems.

## Completion Criteria

You can explain the concepts, select an authorized method, preserve evidence, communicate uncertainty, recommend mitigation, and verify a fix.
