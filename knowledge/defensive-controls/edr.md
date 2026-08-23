---
id: edr
type: defensive-control
name: EDR
status: needs-review
techniques:
  - threat-hunting
  - malware-analysis
  - digital-forensics

related_vulnerabilities:
  - container-security
  - sensitive-data-exposure

sources:
  - https://www.nist.gov/cyberframework
  - https://www.cisecurity.org/controls

---

# EDR

> Endpoint telemetry and response capability for investigating and containing host activity.

## Overview

Endpoint telemetry and response capability for investigating and containing host activity.

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

Container Security, Sensitive Data Exposure

## Related Techniques

Threat Hunting, Malware Analysis, Digital Forensics

## Related Tools

Select tools from the relevant [tool index](../../tools/README.md) and verify their upstream capabilities before deployment.

## Implementation Considerations

Use least privilege, secure defaults, documented change control, protected configuration, and a test that demonstrates the intended outcome.

## Monitoring

Track coverage, control health, policy exceptions, relevant events, response time, and remediation verification. Protect logs and avoid unnecessary personal-data collection.

## References

* [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
* [CIS Critical Security Controls](https://www.cisecurity.org/controls)
