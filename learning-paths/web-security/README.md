---
id: web-security
type: learning-path
name: Web Security
status: needs-review
prerequisites:
  - networking
  - threat-modeling
concepts:
  - http
  - http-requests
  - cookies
  - sessions
  - input-validation
tools:
  - owasp-zap
  - mitmproxy
  - httpie
techniques:
  - security-testing
labs:
  - http-request-analysis
  - api-discovery-local-app
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

# Web Security

> A staged, safety-first learning path.

## Goal

Build a defensible understanding of web security through concepts, controlled practice, evidence, detection, mitigation, and verification.

## Prerequisites

Start with the linked prerequisites and use only owned, synthetic, local, CTF, or explicitly authorized environments.

## Beginner Stage

Study the concepts first, learn the terminology, and complete the first safe lab with a written scope and cleanup plan.

## Intermediate Stage

Use the listed tools against a disposable fixture, record configuration and evidence, and explain false positives, false negatives, limitations, and defensive telemetry.

## Advanced Stage

Design a repeatable assessment or detection exercise, map findings to controls, and verify remediation without expanding beyond authorization.

## Concepts

- [Http](../../knowledge/concepts/http.md)
- [Http Requests](../../knowledge/concepts/http-requests.md)
- [Cookies](../../knowledge/concepts/cookies.md)
- [Sessions](../../knowledge/concepts/sessions.md)
- [Input Validation](../../knowledge/concepts/input-validation.md)

## Techniques

- [Security Testing](../../knowledge/techniques/security-testing.md)

## Tools

- [Owasp Zap](../../tools/web-security/owasp-zap.md)
- [Mitmproxy](../../tools/web-security/mitmproxy.md)
- [Httpie](../../tools/web-security/httpie.md)

## Vulnerabilities

Use the [vulnerability encyclopedia](../../vulnerabilities/README.md) to choose implementation-specific classes rather than assuming a finding.

## Labs

- Http Request Analysis
- Api Discovery Local App

## Defensive Knowledge

Connect each exercise to logging, least privilege, secure configuration, segmentation, and remediation verification.

## Suggested Projects

Create a small, disposable project that documents scope, assumptions, evidence, limitations, controls, cleanup, and completion criteria. Never publish secrets, personal data, malicious payloads, or results from uninvolved systems.

## Completion Criteria

You can explain the concepts, select an authorized method, preserve evidence, communicate uncertainty, recommend mitigation, and verify a fix.
