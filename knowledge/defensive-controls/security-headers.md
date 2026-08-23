---
id: security-headers
type: defensive-control
name: Security Headers
status: needs-review
techniques:
  - web-enumeration
  - security-testing

related_vulnerabilities:
  - cross-site-scripting
  - csrf
  - security-misconfiguration

sources:
  - https://www.nist.gov/cyberframework
  - https://www.cisecurity.org/controls

---

# Security Headers

> HTTP response policies that help constrain browser behavior and reduce web attack surface.

## Overview

HTTP response policies that help constrain browser behavior and reduce web attack surface.

## Purpose

The control reduces a defined class of exposure or improves the organization’s ability to prevent, detect, investigate, or recover from security events.

## What It Protects

Protection may cover systems, identities, data, networks, workloads, or evidence. Define owners, boundaries, and measurable outcomes.

## How It Works

Combine policy, technical enforcement, telemetry, review, and response. A control is not effective merely because a product or setting exists.

## Deployment Considerations

Begin with an inventory and threat model. Test safely, stage changes, document exceptions, protect management access, and plan rollback.

## What It Detects

Detection depends on configuration and telemetry. Validate expected signals with controlled test events and record false positives and blind spots.

## Limitations

Controls reduce risk but do not eliminate it. Coverage, tuning, identity quality, operational ownership, and attacker adaptation remain important.

## Related Vulnerabilities

xss, Csrf, Security Misconfiguration

## Related Techniques

Web Enumeration, Security Testing

## Related Tools

Select tools from the relevant [tool index](../../tools/README.md) and verify their upstream capabilities before deployment.

## Implementation Considerations

Use least privilege, secure defaults, documented change control, protected configuration, and a test that demonstrates the intended outcome.

## Monitoring

Track coverage, control health, policy exceptions, relevant events, response time, and remediation verification. Protect logs and avoid unnecessary personal-data collection.

## References

* [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
* [CIS Critical Security Controls](https://www.cisecurity.org/controls)
