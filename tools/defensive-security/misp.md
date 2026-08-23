---
name: MISP
slug: misp
category: Defensive Security
subcategory: Threat intelligence sharing
difficulty: Intermediate
license: AGPL-3.0
platforms: Linux
language: PHP; JavaScript
repository: https://github.com/MISP/MISP
official_website: https://www.misp-project.org/
documentation: https://www.misp-project.org/documentation/
security_domains: Defensive Security
dual_use: true
concepts:
  - threat-modeling
  - security-monitoring
  - privacy
techniques:
  - threat-intelligence-analysis
  - detection-engineering
technologies:
  - linux
related_vulnerabilities:
  - sensitive-data-exposure
related_labs:
  - localhost-service-inventory
  - packet-capture-fundamentals
defensive_controls:
  - secure-logging
  - data-loss-prevention
  - asset-inventory
related_tools:
  - opencti
  - sigma
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
  - https://github.com/MISP/MISP
  - https://www.misp-project.org/
  - https://www.misp-project.org/documentation/
---

# MISP

> A platform for sharing and correlating threat-intelligence indicators under organizational governance.

## Overview

MISP is a focused security tool for **threat intelligence sharing**. The upstream project and documentation are linked in the metadata; verify current releases, licensing, platform support, and capabilities before production use. This page intentionally marks the entry `needs-review` until a contributor confirms the current upstream facts.

## Tool Metadata

| Property | Details |
| --- | --- |
| Category | Defensive Security |
| Subcategory | Threat intelligence sharing |
| Primary purpose | A platform for sharing and correlating threat-intelligence indicators under organizational governance. |
| License | AGPL-3.0 |
| Platforms | Linux |
| Language | PHP; JavaScript |
| Verification | needs-review; verify against upstream sources |

## Purpose

Use MISP to answer a defined assessment, engineering, or defensive question within an owned, synthetic, local, CTF, or explicitly authorized environment. Record scope, configuration, timestamps, evidence, and limitations.

## Key Features

* Focused support for threat intelligence sharing.
* Repeatable output suitable for review when configuration and scope are retained.
* Integration potential with documented security workflows; confirm exact support upstream.

## How It Works

```mermaid
flowchart LR
    A[Authorized input] --> B[MISP]
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

* Provides a focused workflow for threat intelligence sharing.
* Can produce repeatable evidence for review and remediation.
* Fits into a larger process rather than requiring a new data store.

## Disadvantages

* Results can be incomplete, noisy, version-dependent, or affected by defensive controls.
* Specialist interpretation may be required.
* Collection may expose sensitive information and should be minimized and protected.

## Limitations

MISP cannot establish authorization, attribution, exploitability, or business impact by itself. It does not replace manual validation, threat modeling, secure review, or remediation verification.

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

Monitor for activity consistent with threat intelligence sharing, correlate it with approved change windows and asset inventory, and protect telemetry from unauthorized access. Reduce exposure with least privilege, secure configuration, segmentation, patching, and documented response procedures.

## Alternatives

The related tools are opencti, sigma. Compare scope, evidence quality, platform support, maintenance, licensing, and operational risk rather than relying on unsupported benchmarks.

## Related Knowledge

### Concepts

- [Threat Modeling](../../knowledge/concepts/threat-modeling.md)
- [Security Monitoring](../../knowledge/concepts/security-monitoring.md)
- [Privacy](../../knowledge/concepts/privacy.md)

### Techniques

- [Threat Intelligence Analysis](../../knowledge/techniques/threat-intelligence-analysis.md)
- [Detection Engineering](../../knowledge/techniques/detection-engineering.md)

### Technologies

- [Linux](../../knowledge/technologies/linux.md)

### Vulnerabilities

- [Sensitive Data Exposure](../../vulnerabilities/web/sensitive-data-exposure.md)

### Defensive Controls

- [Secure Logging](../../knowledge/defensive-controls/secure-logging.md)
- [Data Loss Prevention](../../knowledge/defensive-controls/data-loss-prevention.md)
- [Asset Inventory](../../knowledge/defensive-controls/asset-inventory.md)


## References

* [MISP official repository](https://github.com/MISP/MISP)
* [MISP official website](https://www.misp-project.org/)
* [MISP official documentation](https://www.misp-project.org/documentation/)
* [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
