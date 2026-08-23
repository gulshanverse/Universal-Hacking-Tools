---
name: ZMap
slug: zmap
category: Reconnaissance
subcategory: Internet-scale measurement
difficulty: Advanced
license: Apache-2.0
platforms: Linux; macOS
language: C
repository: https://github.com/zmap/zmap
official_website: https://zmap.io/
documentation: https://zmap.io/documentation.html
security_domains: Reconnaissance
dual_use: true
concepts:
  - tcp-ip
  - ports
  - attack-surface
techniques:
  - network-scanning
  - vulnerability-assessment
technologies:
  - linux
related_vulnerabilities:
  - security-misconfiguration
related_labs:
  - localhost-service-inventory
  - packet-capture-fundamentals
defensive_controls:
  - firewall
  - network-segmentation
related_tools:
  - nmap
  - masscan
status: needs-review
verification:
  status: needs-review
  last_verified: 2026-08-23
  status: needs-review
  last_verified: 2026-08-23
sources:
  - https://github.com/zmap/zmap
  - https://zmap.io/
  - https://zmap.io/documentation.html
---

# ZMap

> A high-speed measurement framework that requires strict scope and rate governance.

## Overview

ZMap is a focused security tool for **internet-scale measurement**. The upstream project and documentation are linked in the metadata; verify current releases, licensing, platform support, and capabilities before production use. This page intentionally marks the entry `needs-review` until a contributor confirms the current upstream facts.

## Tool Metadata

| Property | Details |
| --- | --- |
| Category | Reconnaissance |
| Subcategory | Internet-scale measurement |
| Primary purpose | A high-speed measurement framework that requires strict scope and rate governance. |
| License | Apache-2.0 |
| Platforms | Linux, macOS |
| Language | C |
| Verification | needs-review; verify against upstream sources |

## Purpose

Use ZMap to answer a defined assessment, engineering, or defensive question within an owned, synthetic, local, CTF, or explicitly authorized environment. Record scope, configuration, timestamps, evidence, and limitations.

## Key Features

* Focused support for internet-scale measurement.
* Repeatable output suitable for review when configuration and scope are retained.
* Integration potential with documented security workflows; confirm exact support upstream.

## How It Works

```mermaid
flowchart LR
    A[Authorized input] --> B[ZMap]
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

* Provides a focused workflow for internet-scale measurement.
* Can produce repeatable evidence for review and remediation.
* Fits into a larger process rather than requiring a new data store.

## Disadvantages

* Results can be incomplete, noisy, version-dependent, or affected by defensive controls.
* Specialist interpretation may be required.
* Collection may expose sensitive information and should be minimized and protected.

## Limitations

ZMap cannot establish authorization, attribution, exploitability, or business impact by itself. It does not replace manual validation, threat modeling, secure review, or remediation verification.

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

Monitor for activity consistent with internet-scale measurement, correlate it with approved change windows and asset inventory, and protect telemetry from unauthorized access. Reduce exposure with least privilege, secure configuration, segmentation, patching, and documented response procedures.

## Alternatives

The related tools are nmap, masscan. Compare scope, evidence quality, platform support, maintenance, licensing, and operational risk rather than relying on unsupported benchmarks.

## Related Knowledge

### Concepts

- [Tcp Ip](../../knowledge/concepts/tcp-ip.md)
- [Ports](../../knowledge/concepts/ports.md)
- [Attack Surface](../../knowledge/concepts/attack-surface.md)

### Techniques

- [Network Scanning](../../knowledge/techniques/network-scanning.md)
- [Vulnerability Assessment](../../knowledge/techniques/vulnerability-assessment.md)

### Technologies

- [Linux](../../knowledge/technologies/linux.md)

### Vulnerabilities

- [Security Misconfiguration](../../vulnerabilities/configuration/security-misconfiguration.md)

### Defensive Controls

- [Firewall](../../knowledge/defensive-controls/firewall.md)
- [Network Segmentation](../../knowledge/defensive-controls/network-segmentation.md)


## References

* [ZMap official repository](https://github.com/zmap/zmap)
* [ZMap official website](https://zmap.io/)
* [ZMap official documentation](https://zmap.io/documentation.html)
* [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
