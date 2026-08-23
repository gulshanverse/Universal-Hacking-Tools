---
id: session-fixation
type: vulnerability
name: Session Fixation
category: authentication
severity: High
cwe: CWE-384
status: needs-review
affected_technologies:
  - http
related_tools:
  - owasp-zap
  - burp-suite
related_concepts:
  - threat-modeling
  - vulnerability-management
related_techniques:
  - vulnerability-assessment
  - security-testing
related_labs:
  - http-request-analysis
defensive_controls:
  - secure-cookies
  - mfa
  - secure-logging
verification:
  status: needs-review
  confidence: low
  last_verified:
  verification_method: manual-review
  reviewer: repository-audit
  review_notes: Phase 5 metadata audit only; factual claims remain pending claim-level evidence.
sources:
  - https://cwe.mitre.org/
  - https://owasp.org/www-project-top-ten/
---

# Session Fixation

> Defensive knowledge page for an application fails to rotate a session identifier when authentication state changes.

## Description

An application fails to rotate a session identifier when authentication state changes. Assess the concrete implementation and trust boundary; the class name alone does not prove exploitability.

## Severity and Context

High is a context-dependent starting point. Evaluate exposure, preconditions, affected data, exploitability, and business impact using a documented method.

## Root Cause

The root cause is a mismatch between untrusted input or state and the control that should constrain it. Confirm the actual data flow and authorization model.

## Affected Technology

Potentially affected technologies include Sessions, Authentication. Verify the implementation and version before assigning a finding.

## Preconditions

Document the required access, configuration, role, data state, and environmental assumptions. Validate only in a local intentionally vulnerable lab or an explicitly authorized assessment.

## Impact

Potential impact can involve confidentiality, integrity, availability, privacy, compliance, or operational harm. Minimize validation to what is necessary to establish risk.

## Safe Attack Concept

Use a local fixture, synthetic data, or an intentionally vulnerable training application to demonstrate the security boundary. Do not provide payloads or workflows for unrelated systems.

## Detection

Review relevant application, API, identity, network, cloud, endpoint, and configuration telemetry. Add regression tests that prove the intended control and monitor for recurrence.

## Mitigation

Apply Secure Cookies, Mfa, Secure Logging as appropriate. Fix the root cause, use secure defaults, minimize privileges, and verify the fix with a repeatable test.

## Secure Coding Practices

Use threat modeling, context-appropriate validation, safe libraries, explicit authorization, code review, dependency review, and regression tests. Avoid security theater and unsupported claims.

## Safe Lab

Use a disposable local application, synthetic artifact, or approved CTF. Snapshot before testing, protect collected data, and reset the environment afterward.

## Related CWE

[CWE-384](https://cwe.mitre.org/) — verify the precise mapping for the implementation under review.

## Related OWASP Category

Use the current [OWASP Top 10](https://owasp.org/www-project-top-ten/) or relevant OWASP project taxonomy; classifications evolve.

## Related MITRE ATT&CK Technique

Only add an ATT&CK mapping when observed behavior supports it. Consult [MITRE ATT&CK](https://attack.mitre.org/) rather than guessing an ID.

## Related Knowledge

### Concepts

- [Threat Modeling](../../knowledge/concepts/threat-modeling.md)
- [Vulnerability Management](../../knowledge/concepts/vulnerability-management.md)

### Techniques

- [Vulnerability Assessment](../../knowledge/techniques/vulnerability-assessment.md)
- [Security Testing](../../knowledge/techniques/security-testing.md)

### Tools

- [Owasp Zap](../../tools/web-security/owasp-zap.md)
- [Burp Suite](../../tools/web-security/burp-suite.md)

### Defensive Controls

- [Secure Cookies](../../knowledge/defensive-controls/secure-cookies.md)
- [Mfa](../../knowledge/defensive-controls/mfa.md)
- [Secure Logging](../../knowledge/defensive-controls/secure-logging.md)


## References

* [Session Fixation source](https://cwe.mitre.org/data/definitions/384.html)
* [MITRE CWE](https://cwe.mitre.org/)
* [OWASP](https://owasp.org/)
* [NIST Secure Software Development Framework](https://csrc.nist.gov/Projects/ssdf)
