---
id: cross-site-scripting
type: vulnerability
name: Cross-Site Scripting
status: needs-review
verification:
  status: needs-review
  confidence: unknown
  last_verified:
  verification_method: manual-review
  reviewer: repository-audit
  review_notes: Legacy page standardized in Phase 5; claims require future evidence-level review.
sources:
  - https://cwe.mitre.org/
  - https://owasp.org/www-project-top-ten/
  - https://attack.mitre.org/
  - https://owasp.org/
  - https://csrc.nist.gov/Projects/ssdf
---

# Cross-Site Scripting

> Defensive knowledge page for understanding, detecting, and mitigating cross-site scripting.

## Description

Untrusted data is interpreted as active content in a user agent.

## Severity and Context

Severity depends on exposure, preconditions, affected data, exploitability, and business impact. Use a documented risk method such as CVSS where appropriate; do not assign a universal score without context.

## Root Cause

The root cause is a mismatch between untrusted input or an untrusted state and the security boundary that should constrain it. Confirm the actual data flow and trust assumptions during review.

## Affected Technology

Web applications, APIs, identity systems, infrastructure, cloud services, or software supply chains may be affected depending on the specific implementation.

## Preconditions

Document the required access, configuration, user role, data state, and environmental assumptions. Keep validation within a local intentionally vulnerable lab or an authorized assessment.

## Impact

Potential impact may include confidentiality, integrity, availability, privacy, compliance, or operational harm. Assess only what is necessary to establish risk.

## Safe Attack Concept

Teach the concept with a local fixture such as OWASP Juice Shop, WebGoat, DVWA, a test API, or synthetic code. Do not provide payloads or workflows for unrelated targets.

## Detection

Review application logs, access-control decisions, validation failures, unusual request patterns, identity events, cloud audit records, dependency data, and endpoint telemetry relevant to the vulnerability. Add regression tests that prove the security boundary.

## Mitigation

Use contextual output encoding, safe templating, input handling, and an appropriate Content Security Policy.

## Secure Coding Practices

Use threat modeling, secure defaults, explicit authorization, input validation appropriate to context, safe libraries, dependency review, code review, and automated regression tests.

## Safe Lab

Use an isolated local lab and synthetic data. Define the learning objective, take a snapshot before testing, record expected observations, and reset the environment afterward.

## Related CWE

[CWE-79](https://cwe.mitre.org/) — verify the exact mapping for the implementation under review.

## Related OWASP Category

Map to the current [OWASP Top 10](https://owasp.org/www-project-top-ten/) or relevant OWASP project category; taxonomies evolve.

## Related MITRE ATT&CK Technique

A technique mapping is context-dependent. Use the [MITRE ATT&CK](https://attack.mitre.org/) knowledge base only when the observed behavior supports the mapping.

## References

* [MITRE CWE](https://cwe.mitre.org/)
* [OWASP](https://owasp.org/)
* [NIST Secure Software Development Framework](https://csrc.nist.gov/Projects/ssdf)

## Related Knowledge

### Concepts

- [Threat Modeling](../../knowledge/concepts/threat-modeling.md)
- [Vulnerability Management](../../knowledge/concepts/vulnerability-management.md)

### Techniques

- [Vulnerability Assessment](../../knowledge/techniques/vulnerability-assessment.md)
- [Security Testing](../../knowledge/techniques/security-testing.md)

### Technologies

- [HTTP](../../knowledge/technologies/http.md)
- [REST APIs](../../knowledge/technologies/rest-apis.md)

### Tools

- [OWASP ZAP](../../tools/web-security/owasp-zap.md)
- [Burp Suite](../../tools/web-security/burp-suite.md)

### Labs

- [HTTP Request Analysis](../../labs/web/http-request-analysis.md)

### Defensive Controls

- [Secure Logging](../../knowledge/defensive-controls/secure-logging.md)
- [Secure Configuration](../../knowledge/defensive-controls/secure-configuration.md)
