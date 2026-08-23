---
name: Velociraptor
slug: velociraptor
category: Defensive Security
subcategory: Endpoint visibility
difficulty: Advanced
license: AGPL-3.0
platforms: Linux; Windows; macOS
language: Go
repository: https://github.com/Velocidex/velociraptor
official_website: https://docs.velociraptor.app/
documentation: https://docs.velociraptor.app/
security_domains: Defensive Security
dual_use: true
concepts:
  - security-monitoring
  - processes
techniques:
  - threat-hunting
  - digital-forensics
  - incident-triage
technologies:
  - linux
  - windows
  - macos
related_vulnerabilities:
  - sensitive-data-exposure
  - security-misconfiguration
related_labs:
  - localhost-service-inventory
  - packet-capture-fundamentals
defensive_controls:
  - edr
  - secure-logging
  - endpoint-detection
related_tools:
  - osquery
  - wazuh
status: needs-review
verification:
  status: needs-review
  last_verified: 2026-08-23
sources:
  - https://github.com/Velocidex/velociraptor
  - https://docs.velociraptor.app/
  - https://docs.velociraptor.app/
---

# Velociraptor

> A digital-forensics and endpoint-visibility platform for authorized investigations.

## Overview

Velociraptor is a focused security tool for **endpoint visibility**. The upstream project and documentation are linked in the metadata; verify current releases, licensing, platform support, and capabilities before production use. This page intentionally marks the entry `needs-review` until a contributor confirms the current upstream facts.

## Tool Metadata

| Property | Details |
| --- | --- |
| Category | Defensive Security |
| Subcategory | Endpoint visibility |
| Primary purpose | A digital-forensics and endpoint-visibility platform for authorized investigations. |
| License | AGPL-3.0 |
| Platforms | Linux, Windows, macOS |
| Language | Go |
| Verification | needs-review; verify against upstream sources |

## Purpose

Use Velociraptor to answer a defined assessment, engineering, or defensive question within an owned, synthetic, local, CTF, or explicitly authorized environment. Record scope, configuration, timestamps, evidence, and limitations.

## Key Features

* Focused support for endpoint visibility.
* Repeatable output suitable for review when configuration and scope are retained.
* Integration potential with documented security workflows; confirm exact support upstream.

## How It Works

```mermaid
flowchart LR
    A[Authorized input] --> B[Velociraptor]
    B --> C[Analysis or collection]
    C --> D[Evidence]
    D --> E[Validation]
    E --> F[Remediation or detection]
```

The tool’s behavior depends on version, configuration, permissions, data quality, and environment. Output is an observation, not proof of compromise or business impact.

## Installation

Follow the official repository or documentation links above. Do not copy unverified commands or install unknown packages. Prefer a disposable virtual machine or container for learning.

## Safe Usage

Use only local fixtures, intentionally vulnerable applications, synthetic data, owned infrastructure, CTFs, or written authorized assessments. Do not test unrelated public systems, accounts, devices, or data.

## Advantages

* Provides a focused workflow for endpoint visibility.
* Can produce repeatable evidence for review and remediation.
* Fits into a larger process rather than requiring a new data store.

## Disadvantages

* Results can be incomplete, noisy, version-dependent, or affected by defensive controls.
* Specialist interpretation may be required.
* Collection may expose sensitive information and should be minimized and protected.

## Limitations

Velociraptor cannot establish authorization, attribution, exploitability, or business impact by itself. It does not replace manual validation, threat modeling, secure review, or remediation verification.

> **SECURITY / LEGAL NOTICE**
>
> Use this tool only on systems, applications, networks, accounts, devices, or data that you own or have explicit authorization to assess. Unauthorized scanning, exploitation, credential testing, interception, or access may be illegal.


## Basic Usage in a Safe Lab

Create a disposable fixture, define the smallest authorized scope, record the configuration, and preserve only the evidence needed for the learning objective.

## Intermediate Usage

In an approved assessment, compare the result with a known baseline, document false positives and false negatives, and correlate observations with asset ownership and telemetry.

## Advanced Concepts

Consider versioning, permissions, rate limits, data provenance, output validation, and operational risk before incorporating this workflow into a larger program.

## Mitigation

Use the findings to improve secure configuration, least privilege, segmentation, patching, protected logging, and remediation verification as appropriate to the system.


## Defensive Perspective

Defenders should understand the activity the tool could produce without attempting evasion. Review relevant network, application, endpoint, identity, cloud, or file telemetry and define a safe test event before relying on a detection.

## Detection and Mitigation

Monitor for activity consistent with endpoint visibility, correlate it with approved change windows and asset inventory, and protect telemetry from unauthorized access. Reduce exposure with least privilege, secure configuration, segmentation, patching, and documented response procedures.

## Alternatives

The related tools are osquery, wazuh. Compare scope, evidence quality, platform support, maintenance, licensing, and operational risk rather than relying on unsupported benchmarks.

## Related Knowledge

### Concepts

- [Security Monitoring](../../knowledge/concepts/security-monitoring.md)
- [Digital Forensics](../../knowledge/techniques/digital-forensics.md)
- [Processes](../../knowledge/concepts/processes.md)

### Techniques

- [Threat Hunting](../../knowledge/techniques/threat-hunting.md)
- [Digital Forensics](../../knowledge/techniques/digital-forensics.md)
- [Incident Triage](../../knowledge/techniques/incident-triage.md)

### Technologies

- [Linux](../../knowledge/technologies/linux.md)
- [Windows](../../knowledge/technologies/windows.md)
- [Macos](../../knowledge/technologies/macos.md)

### Vulnerabilities

- [Sensitive Data Exposure](../../vulnerabilities/web/sensitive-data-exposure.md)
- [Security Misconfiguration](../../vulnerabilities/configuration/security-misconfiguration.md)

### Defensive Controls

- [Edr](../../knowledge/defensive-controls/edr.md)
- [Secure Logging](../../knowledge/defensive-controls/secure-logging.md)
- [Endpoint Detection](../../knowledge/defensive-controls/endpoint-detection.md)


## References

* [Velociraptor official repository](https://github.com/Velocidex/velociraptor)
* [Velociraptor official website](https://docs.velociraptor.app/)
* [Velociraptor official documentation](https://docs.velociraptor.app/)
* [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
