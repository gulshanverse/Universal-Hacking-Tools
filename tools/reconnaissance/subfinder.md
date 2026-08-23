---
name: Subfinder
slug: subfinder
category: Reconnaissance
subcategory: Subdomain discovery
difficulty: Beginner
license: MIT
platforms: [Linux; Windows; macOS]
language: Go
repository: https://github.com/projectdiscovery/subfinder
official_website: https://projectdiscovery.io/opensource/subfinder
documentation: https://docs.projectdiscovery.io/tools/subfinder/overview
security_domains: [Reconnaissance, Subdomain discovery]
dual_use: true

concepts:
  - attack-surface
  - dns
  - networking
  - ports
  - services
  - tcp-ip
techniques:
  - dns-enumeration
  - network-scanning
  - service-enumeration
  - subdomain-discovery
technologies:
  - dns
  - linux
  - macos
  - windows
related_tools:
  - amass
  - nmap
  - theharvester
related_vulnerabilities:
  - security-misconfiguration
related_labs:
  - localhost-service-inventory
  - packet-capture-fundamentals
defensive_controls:
  - firewall
  - network-segmentation
  - secure-logging
verification:
  status: needs-review
  confidence: low
  verification_method: manual-review
  reviewer: repository-audit
  review_notes: Phase 5 metadata audit only; factual claims remain pending claim-level evidence.
  status: partially-verified
  last_verified: 2026-08-23
sources:
  official_repository: https://github.com/projectdiscovery/subfinder
  official_website: https://projectdiscovery.io/opensource/subfinder
  official_documentation: https://docs.projectdiscovery.io/tools/subfinder/overview
status: Verify against upstream documentation.
---

# Subfinder

> Passive subdomain discovery. This page is written for lawful, authorized security education.

## Overview

**Subfinder** is used for fast, passive discovery using public sources with emphasis on scope control and data quality. Its value depends on clear authorization, a defined scope, and a documented assessment objective. It should be treated as one component of a broader workflow rather than as proof that a finding is exploitable or material.

The project’s upstream repository, official website, and documentation are linked in the metadata above. Maintenance status, release versions, and feature details can change; verify those items upstream before relying on them in production.

## Tool Metadata

| Property | Details |
| --- | --- |
| Category | Reconnaissance |
| Subcategory | Subdomain discovery |
| Primary purpose | Passive subdomain discovery |
| License | MIT |
| Open source | Verify upstream; edition and component terms may differ. |
| Platform | Linux; Windows; macOS |
| Language | Go |
| Repository | [Subfinder repository](https://github.com/projectdiscovery/subfinder) |
| Official website | [https://projectdiscovery.io/opensource/subfinder](https://projectdiscovery.io/opensource/subfinder) |
| Documentation | [https://docs.projectdiscovery.io/tools/subfinder/overview](https://docs.projectdiscovery.io/tools/subfinder/overview) |
| Current version | Not recorded here; verify upstream. |
| Difficulty | Beginner |
| Security domain | Reconnaissance; Subdomain discovery |
| Defensive / offensive / both | Both; use only within authorization. |

## Purpose

Use Subfinder when the assessment question matches **passive subdomain discovery**. A professional workflow normally records the asset or artifact, authorization, time window, operator, configuration, result, confidence, and remediation owner.

## Key Features

* Fast, passive discovery using public sources with emphasis on scope control and data quality.
* Structured output or evidence that can be reviewed by another analyst, subject to the tool’s actual capabilities and configuration.
* Integration into a larger workflow through documented files, APIs, plugins, or reports where supported upstream.
* Repeatable use in a local lab or approved environment with explicit scope and rate controls.

## How It Works

At a high level, the workflow is:

```mermaid
flowchart LR
    A[Authorized scope or artifact] --> B[Subfinder]
    B --> C[Collection or analysis]
    C --> D[Evidence and observations]
    D --> E[Analyst validation]
    E --> F[Report and remediation]
```

The inputs, processing model, and outputs vary by version and configuration. Treat output as an observation that requires validation, not as an automatic vulnerability, attribution, or compromise conclusion.

## Installation

Use the official installation guidance linked in **Tool Metadata**. Package names, binaries, dependencies, and supported platforms can change. Do not copy installation commands from unverified third-party pages. For a safe learning environment, prefer a disposable virtual machine, container, or operating-system package that you can update and remove.

## Basic Usage in a Safe Lab

Start with a local service, synthetic file, packet capture, test account, intentionally vulnerable application, or other artifact that you own. Define the scope before launching the tool, keep request or capture rates conservative, and save the output with a timestamp. Do not use unrelated public domains, addresses, accounts, or data as examples.

## Intermediate Usage

In an approved assessment, connect the tool’s output to an asset inventory and a repeatable evidence process. Record the exact scope, configuration, exclusions, timestamps, relevant output, analyst interpretation, and a remediation recommendation. Common mistakes include treating a match as proof, overlooking false positives, ignoring rate limits, and failing to protect collected data.

## Advanced Concepts

Advanced use should focus on measurement quality, reproducibility, parser or rule review, coverage gaps, and the relationship between collection and defensive telemetry. Where the tool supports automation, test it against a controlled fixture first and add a stop condition. Avoid evasion, persistence, credential abuse, destructive actions, and any activity against uninvolved systems.

## Real-World Use Cases

Legitimate uses include security audits, vulnerability management, incident response, asset inventory, threat hunting, secure development, compliance evidence, and security research performed under written authorization. The correct use case depends on the tool configuration and the organization’s rules of engagement.

## Advantages

* Focused workflow for passive subdomain discovery.
* Useful evidence for review when outputs are retained with scope and configuration.
* Can support repeatable lab exercises and documented professional processes.
* Benefits from the upstream project’s ecosystem; verify current integrations and maintenance status.

## Disadvantages

* Results may contain false positives, false negatives, or incomplete coverage.
* Performance and behavior depend on target size, configuration, network conditions, and version.
* Some capabilities require specialist knowledge, elevated permissions, or edition-specific features.
* Collection may expose sensitive data and can trigger defensive controls even when authorized.

## Limitations

Subfinder cannot replace authorization, asset ownership, threat modeling, manual validation, secure coding review, incident-response judgment, or remediation verification. It does not establish attribution or business impact by itself.

> **SECURITY / LEGAL NOTICE**
>
> Use this tool only on systems, applications, networks, accounts, devices, or data that you own or have explicit authorization to assess. Unauthorized scanning, exploitation, credential testing, interception, or access may be illegal.

## Defensive Perspective

For reconnaissance, defenders should understand the observable activity without attempting to evade it. Review DNS, firewall, proxy, and scan telemetry; compare findings with the authorized inventory. Limit exposure, remove unintended services, enforce segmentation, and continuously reconcile discovered assets.

## Detection

Review DNS, firewall, proxy, and scan telemetry; compare findings with the authorized inventory. Useful telemetry may include application or service logs, DNS and network records, endpoint process events, identity events, cloud audit logs, or file-integrity data, depending on the tool and the environment. Establish a known-good baseline before interpreting anomalies.

## Mitigation

Limit exposure, remove unintended services, enforce segmentation, and continuously reconcile discovered assets. Document ownership, severity, compensating controls, and verification criteria. Re-test only within the approved scope.

## Alternatives

| Tool or method | Best for | Difficulty | License |
| --- | --- | --- | --- |
| Amass | A related workflow or comparison point | Verify upstream | Verify upstream |
| theHarvester | Complementary analysis | Verify upstream | Verify upstream |
| crt.sh | Validation or defense | Verify upstream | Verify upstream |

## Comparison Guidance

Compare tools using scope control, coverage, evidence quality, platform support, maintainability, reporting, integration, and total operational risk. Do not infer benchmark results from this page; measure in a representative authorized lab when performance matters.

## When to Use

Use Subfinder when the objective is clearly defined, the data or target is authorized, the expected output is understood, and a reviewer can reproduce the observation.

## When Not to Use

Do not use it against unrelated public infrastructure, personal accounts, production systems without approval, or data that you are not permitted to collect. Choose another method when the question requires a different evidence source or when the tool’s coverage is not appropriate.

## Common Mistakes

* Starting without written scope, an owner, or a stop condition.
* Treating an automated result as a confirmed finding.
* Failing to record configuration, version, timestamps, and exclusions.
* Exposing collected data in tickets, logs, or public repositories.
* Ignoring maintenance status, licensing, platform constraints, or downstream risk.

## Safe Practice Lab

Use a local virtual machine, disposable container, synthetic dataset, packet capture, or intentionally vulnerable platform such as **OWASP Juice Shop**, **DVWA**, **WebGoat**, or a CTF environment. Keep the lab isolated, use test identities, and destroy or reset it after the exercise. Maintain an approved asset list, rate limits, collection timestamps, and a clear stop condition.

## Learning Exercises

1. **Beginner:** Identify the tool’s scope, inputs, outputs, and one limitation using a local lab fixture.
2. **Intermediate:** Repeat the exercise with documented configuration, timestamps, and a false-positive review.
3. **Advanced:** Map an observation to a defensive control, detection source, remediation owner, and verification test.

## Related Concepts

* Reconnaissance
* Subdomain discovery
* Authorization and rules of engagement
* Evidence handling and reproducibility
* Detection and mitigation

## Related Tools

See the related category index in [`tools/reconnaissance/README.md`](../reconnaissance/README.md) and compare with the alternatives listed above.

## Related Defensive Controls

* Asset inventory and least privilege
* Network or workload segmentation
* Centralized, access-controlled logging
* Secure configuration and patch management
* Detection validation and incident-response procedures

## Related Labs

* [`labs/README.md`](../../labs/README.md)
* [`Localhost network and service inventory`](../../labs/networking/localhost-service-inventory.md)
* [`Evidence-first analysis workflow`](../../labs/forensics/evidence-first-analysis.md)

## References

1. [Subfinder official repository](https://github.com/projectdiscovery/subfinder)
2. [Subfinder official website](https://projectdiscovery.io/opensource/subfinder)
3. [Subfinder official documentation](https://docs.projectdiscovery.io/tools/subfinder/overview)
4. [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
5. [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)

> Verify upstream documentation for current versions, installation instructions, capabilities, licenses, and platform support before use.
## Related Knowledge

### Concepts

- [Networking](../../knowledge/concepts/networking.md)
- [TCP/IP](../../knowledge/concepts/tcp-ip.md)
- [DNS](../../knowledge/concepts/dns.md)
- [Ports](../../knowledge/concepts/ports.md)
- [Services](../../knowledge/concepts/services.md)
- [Attack Surface](../../knowledge/concepts/attack-surface.md)

### Techniques

- [Network Scanning](../../knowledge/techniques/network-scanning.md)
- [Service Enumeration](../../knowledge/techniques/service-enumeration.md)
- [DNS Enumeration](../../knowledge/techniques/dns-enumeration.md)
- [Subdomain Discovery](../../knowledge/techniques/subdomain-discovery.md)

### Technologies

- [Linux](../../knowledge/technologies/linux.md)
- [Windows](../../knowledge/technologies/windows.md)
- [macOS](../../knowledge/technologies/macos.md)
- [DNS](../../knowledge/technologies/dns.md)

### Vulnerabilities

- [Security Misconfiguration](../../vulnerabilities/configuration/security-misconfiguration.md)

### Labs

- [Localhost Service Inventory](../../labs/networking/localhost-service-inventory.md)
- [Packet Capture Fundamentals](../../labs/networking/packet-capture-fundamentals.md)

### Defensive Controls

- [Firewall](../../knowledge/defensive-controls/firewall.md)
- [Network Segmentation](../../knowledge/defensive-controls/network-segmentation.md)
- [Secure Logging](../../knowledge/defensive-controls/secure-logging.md)

### Related Tools

- [nmap](nmap.md)
- [amass](amass.md)
- [theharvester](theharvester.md)
