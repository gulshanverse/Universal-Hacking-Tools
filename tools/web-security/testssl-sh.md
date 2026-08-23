---
name: testssl.sh
slug: testssl-sh
category: Web Security
subcategory: TLS configuration assessment
difficulty: Intermediate
license: GPL-2.0
platforms: Linux; macOS; Windows
language: Shell
repository: https://github.com/drwetter/testssl.sh
official_website: https://testssl.sh/
documentation: https://testssl.sh/Documentation/
security_domains: Web Security
dual_use: true
concepts:
  - tls
  - https
  - cryptography
  - certificates
techniques:
  - security-testing
  - vulnerability-assessment
technologies:
  - linux
  - windows
  - macos
  - tls
related_vulnerabilities:
  - cryptographic-failures
  - security-misconfiguration
related_labs:
  - localhost-service-inventory
  - packet-capture-fundamentals
defensive_controls:
  - encryption
  - secure-configuration
  - secure-logging
related_tools:
  - wireshark
  - owasp-zap
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
  - https://github.com/drwetter/testssl.sh
  - https://testssl.sh/
  - https://testssl.sh/Documentation/
---

# testssl.sh

> A command-line tool for examining TLS configuration in approved environments.

## Overview

testssl.sh is a focused security tool for **tls configuration assessment**. The upstream project and documentation are linked in the metadata; verify current releases, licensing, platform support, and capabilities before production use. This page intentionally marks the entry `needs-review` until a contributor confirms the current upstream facts.

## Tool Metadata

| Property | Details |
| --- | --- |
| Category | Web Security |
| Subcategory | TLS configuration assessment |
| Primary purpose | A command-line tool for examining TLS configuration in approved environments. |
| License | GPL-2.0 |
| Platforms | Linux, macOS, Windows |
| Language | Shell |
| Verification | needs-review; verify against upstream sources |

## Purpose

Use testssl.sh to answer a defined assessment, engineering, or defensive question within an owned, synthetic, local, CTF, or explicitly authorized environment. Record scope, configuration, timestamps, evidence, and limitations.

## Key Features

* Focused support for tls configuration assessment.
* Repeatable output suitable for review when configuration and scope are retained.
* Integration potential with documented security workflows; confirm exact support upstream.

## How It Works

```mermaid
flowchart LR
    A[Authorized input] --> B[testssl.sh]
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

* Provides a focused workflow for tls configuration assessment.
* Can produce repeatable evidence for review and remediation.
* Fits into a larger process rather than requiring a new data store.

## Disadvantages

* Results can be incomplete, noisy, version-dependent, or affected by defensive controls.
* Specialist interpretation may be required.
* Collection may expose sensitive information and should be minimized and protected.

## Limitations

testssl.sh cannot establish authorization, attribution, exploitability, or business impact by itself. It does not replace manual validation, threat modeling, secure review, or remediation verification.

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

Monitor for activity consistent with tls configuration assessment, correlate it with approved change windows and asset inventory, and protect telemetry from unauthorized access. Reduce exposure with least privilege, secure configuration, segmentation, patching, and documented response procedures.

## Alternatives

The related tools are wireshark, owasp-zap. Compare scope, evidence quality, platform support, maintenance, licensing, and operational risk rather than relying on unsupported benchmarks.

## Related Knowledge

### Concepts

- [Tls](../../knowledge/concepts/tls.md)
- [Https](../../knowledge/concepts/https.md)
- [Cryptography](../../knowledge/concepts/cryptography.md)
- [Certificates](../../knowledge/concepts/certificates.md)

### Techniques

- [Security Testing](../../knowledge/techniques/security-testing.md)
- [Vulnerability Assessment](../../knowledge/techniques/vulnerability-assessment.md)

### Technologies

- [Linux](../../knowledge/technologies/linux.md)
- [Windows](../../knowledge/technologies/windows.md)
- [Macos](../../knowledge/technologies/macos.md)
- [Tls](../../knowledge/technologies/tls.md)

### Vulnerabilities

- [Cryptographic Failures](../../vulnerabilities/cryptography/cryptographic-failures.md)
- [Security Misconfiguration](../../vulnerabilities/configuration/security-misconfiguration.md)

### Defensive Controls

- [Encryption](../../knowledge/defensive-controls/encryption.md)
- [Secure Configuration](../../knowledge/defensive-controls/secure-configuration.md)
- [Secure Logging](../../knowledge/defensive-controls/secure-logging.md)


## References

* [testssl.sh official repository](https://github.com/drwetter/testssl.sh)
* [testssl.sh official website](https://testssl.sh/)
* [testssl.sh official documentation](https://testssl.sh/Documentation/)
* [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
