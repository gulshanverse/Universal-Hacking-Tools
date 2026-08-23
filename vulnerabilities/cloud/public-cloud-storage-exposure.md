---
id: public-cloud-storage-exposure
type: vulnerability
name: Public Cloud Storage Exposure
category: cloud
severity: High
cwe: CWE-668
status: needs-review
affected_technologies:
  - aws
  - azure
  - gcp
related_tools:
  - prowler
  - trivy
related_concepts:
  - threat-modeling
  - vulnerability-management
related_techniques:
  - vulnerability-assessment
  - security-testing
related_labs:
  - http-request-analysis
defensive_controls:
  - least-privilege
  - secure-configuration
  - data-loss-prevention
sources:
  - https://cwe.mitre.org/
  - https://owasp.org/www-project-top-ten/
---

# Public Cloud Storage Exposure

> Defensive knowledge page for cloud storage is reachable or readable more broadly than the data owner intended.

## Description

Cloud storage is reachable or readable more broadly than the data owner intended. Assess the concrete implementation and trust boundary; the class name alone does not prove exploitability.

## Severity and Context

High is a context-dependent starting point. Evaluate exposure, preconditions, affected data, exploitability, and business impact using a documented method.

## Root Cause

The root cause is a mismatch between untrusted input or state and the control that should constrain it. Confirm the actual data flow and authorization model.

## Affected Technology

Potentially affected technologies include Aws, Azure, Gcp, Data Classification. Verify the implementation and version before assigning a finding.

## Preconditions

Document the required access, configuration, role, data state, and environmental assumptions. Validate only in a local intentionally vulnerable lab or an explicitly authorized assessment.

## Impact

Potential impact can involve confidentiality, integrity, availability, privacy, compliance, or operational harm. Minimize validation to what is necessary to establish risk.

## Safe Attack Concept

Use a local fixture, synthetic data, or an intentionally vulnerable training application to demonstrate the security boundary. Do not provide payloads or workflows for unrelated systems.

## Detection

Review relevant application, API, identity, network, cloud, endpoint, and configuration telemetry. Add regression tests that prove the intended control and monitor for recurrence.

## Mitigation

Apply Least Privilege, Secure Configuration, Data Loss Prevention as appropriate. Fix the root cause, use secure defaults, minimize privileges, and verify the fix with a repeatable test.

## Secure Coding Practices

Use threat modeling, context-appropriate validation, safe libraries, explicit authorization, code review, dependency review, and regression tests. Avoid security theater and unsupported claims.

## Safe Lab

Use a disposable local application, synthetic artifact, or approved CTF. Snapshot before testing, protect collected data, and reset the environment afterward.

## Related CWE

[CWE-668](https://cwe.mitre.org/) — verify the precise mapping for the implementation under review.

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

- [Prowler](../../tools/cloud-security/prowler.md)
- [Trivy](../../tools/vulnerability-management/trivy.md)

### Defensive Controls

- [Least Privilege](../../knowledge/defensive-controls/least-privilege.md)
- [Secure Configuration](../../knowledge/defensive-controls/secure-configuration.md)
- [Data Loss Prevention](../../knowledge/defensive-controls/data-loss-prevention.md)


## References

* [Public Cloud Storage Exposure source](https://cwe.mitre.org/data/definitions/668.html)
* [MITRE CWE](https://cwe.mitre.org/)
* [OWASP](https://owasp.org/)
* [NIST Secure Software Development Framework](https://csrc.nist.gov/Projects/ssdf)
