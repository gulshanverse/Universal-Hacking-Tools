---
id: weak-key-management
type: vulnerability
name: Weak Key Management
category: cryptography
severity: High
cwe: CWE-320
status: needs-review
affected_technologies:
  - tls
related_tools:
  - testssl-sh
  - semgrep
related_concepts:
  - threat-modeling
  - vulnerability-management
related_techniques:
  - vulnerability-assessment
  - security-testing
related_labs:
  - http-request-analysis
defensive_controls:
  - encryption
  - secrets-management
  - least-privilege
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

# Weak Key Management

> Defensive knowledge page for cryptographic keys are generated, stored, used, or retired without adequate lifecycle controls.

## Description

Cryptographic keys are generated, stored, used, or retired without adequate lifecycle controls. Assess the concrete implementation and trust boundary; the class name alone does not prove exploitability.

## Severity and Context

High is a context-dependent starting point. Evaluate exposure, preconditions, affected data, exploitability, and business impact using a documented method.

## Root Cause

The root cause is a mismatch between untrusted input or state and the control that should constrain it. Confirm the actual data flow and authorization model.

## Affected Technology

Potentially affected technologies include Cryptography, Key Management, Encryption. Verify the implementation and version before assigning a finding.

## Preconditions

Document the required access, configuration, role, data state, and environmental assumptions. Validate only in a local intentionally vulnerable lab or an explicitly authorized assessment.

## Impact

Potential impact can involve confidentiality, integrity, availability, privacy, compliance, or operational harm. Minimize validation to what is necessary to establish risk.

## Safe Attack Concept

Use a local fixture, synthetic data, or an intentionally vulnerable training application to demonstrate the security boundary. Do not provide payloads or workflows for unrelated systems.

## Detection

Review relevant application, API, identity, network, cloud, endpoint, and configuration telemetry. Add regression tests that prove the intended control and monitor for recurrence.

## Mitigation

Apply Encryption, Secrets Management, Least Privilege as appropriate. Fix the root cause, use secure defaults, minimize privileges, and verify the fix with a repeatable test.

## Secure Coding Practices

Use threat modeling, context-appropriate validation, safe libraries, explicit authorization, code review, dependency review, and regression tests. Avoid security theater and unsupported claims.

## Safe Lab

Use a disposable local application, synthetic artifact, or approved CTF. Snapshot before testing, protect collected data, and reset the environment afterward.

## Related CWE

[CWE-320](https://cwe.mitre.org/) — verify the precise mapping for the implementation under review.

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

- [Testssl Sh](../../tools/web-security/testssl-sh.md)
- [Semgrep](../../tools/secure-development/semgrep.md)

### Defensive Controls

- [Encryption](../../knowledge/defensive-controls/encryption.md)
- [Secrets Management](../../knowledge/defensive-controls/secrets-management.md)
- [Least Privilege](../../knowledge/defensive-controls/least-privilege.md)


## References

* [Weak Key Management source](https://cwe.mitre.org/data/definitions/320.html)
* [MITRE CWE](https://cwe.mitre.org/)
* [OWASP](https://owasp.org/)
* [NIST Secure Software Development Framework](https://csrc.nist.gov/Projects/ssdf)
