---
name: Naabu
slug: naabu
category: Reconnaissance
subcategory: Port scanning
difficulty: Intermediate
license: MIT
platforms: Linux; Windows; macOS
language: Go
repository: https://github.com/projectdiscovery/naabu
official_website: https://projectdiscovery.io/opensource/naabu
documentation: https://docs.projectdiscovery.io/tools/naabu/overview
security_domains: Reconnaissance
dual_use: true
concepts:
  - ports
  - services
  - attack-surface
techniques:
  - network-scanning
  - service-enumeration
technologies:
  - linux
  - windows
related_vulnerabilities:
  - security-misconfiguration
related_labs:
  - localhost-service-inventory
  - packet-capture-fundamentals
defensive_controls:
  - firewall
  - network-segmentation
  - secure-logging
related_tools:
  - nmap
  - masscan
status: needs-review
verification:
  status: needs-review
  confidence: low
  verification_method: manual-review
  reviewer: repository-audit
  review_notes: Phase 5 metadata audit only; factual claims remain pending claim-level evidence.
  status: needs-review
  last_verified: 2026-08-23
  status: needs-review
  last_verified: 2026-08-23
sources:
  - https://github.com/projectdiscovery/naabu
  - https://projectdiscovery.io/opensource/naabu
  - https://docs.projectdiscovery.io/tools/naabu/overview
---

# Naabu

> A focused port scanner for approved asset inventories.

## Overview

Naabu is a focused security tool for **port scanning**. The upstream project and documentation are linked in the metadata; verify current releases, licensing, platform support, and capabilities before production use. This page intentionally marks the entry `needs-review` until a contributor confirms the current upstream facts.

## Tool Metadata

| Property | Details |
| --- | --- |
| Category | Reconnaissance |
| Subcategory | Port scanning |
| Primary purpose | A focused port scanner for approved asset inventories. |
| License | MIT |
| Platforms | Linux, Windows, macOS |
| Language | Go |
| Verification | needs-review; verify against upstream sources |

## Purpose

Use Naabu to answer a defined assessment, engineering, or defensive question within an owned, synthetic, local, CTF, or explicitly authorized environment. Record scope, configuration, timestamps, evidence, and limitations.

## Key Features

* Focused support for port scanning.
* Repeatable output suitable for review when configuration and scope are retained.
* Integration potential with documented security workflows; confirm exact support upstream.

## How It Works

```mermaid
flowchart LR
    A[Authorized input] --> B[Naabu]
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

* Provides a focused workflow for port scanning.
* Can produce repeatable evidence for review and remediation.
* Fits into a larger process rather than requiring a new data store.

## Disadvantages

* Results can be incomplete, noisy, version-dependent, or affected by defensive controls.
* Specialist interpretation may be required.
* Collection may expose sensitive information and should be minimized and protected.

## Limitations

Naabu cannot establish authorization, attribution, exploitability, or business impact by itself. It does not replace manual validation, threat modeling, secure review, or remediation verification.

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

Monitor for activity consistent with port scanning, correlate it with approved change windows and asset inventory, and protect telemetry from unauthorized access. Reduce exposure with least privilege, secure configuration, segmentation, patching, and documented response procedures.

## Alternatives

The related tools are nmap, masscan. Compare scope, evidence quality, platform support, maintenance, licensing, and operational risk rather than relying on unsupported benchmarks.

## Related Knowledge

### Concepts

- [Ports](../../knowledge/concepts/ports.md)
- [Services](../../knowledge/concepts/services.md)
- [Attack Surface](../../knowledge/concepts/attack-surface.md)

### Techniques

- [Network Scanning](../../knowledge/techniques/network-scanning.md)
- [Service Enumeration](../../knowledge/techniques/service-enumeration.md)

### Technologies

- [Linux](../../knowledge/technologies/linux.md)
- [Windows](../../knowledge/technologies/windows.md)

### Vulnerabilities

- [Security Misconfiguration](../../vulnerabilities/configuration/security-misconfiguration.md)

### Defensive Controls

- [Firewall](../../knowledge/defensive-controls/firewall.md)
- [Network Segmentation](../../knowledge/defensive-controls/network-segmentation.md)
- [Secure Logging](../../knowledge/defensive-controls/secure-logging.md)


## References

* [Naabu official repository](https://github.com/projectdiscovery/naabu)
* [Naabu official website](https://projectdiscovery.io/opensource/naabu)
* [Naabu official documentation](https://docs.projectdiscovery.io/tools/naabu/overview)
* [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
