---
id: reverse-engineering
type: technique
name: Reverse Engineering
status: needs-review
concepts:
  - threat-modeling
  - security-monitoring
tools:
  - ghidra
  - radare2
  - cutter
technologies:
  - linux
related_vulnerabilities:
  - api-security
  - authentication-weaknesses
  - broken-access-control
  - cloud-misconfiguration
  - command-injection
  - container-security
defensive_controls:
  - endpoint-detection
  - secure-logging

sources:
  - https://www.nist.gov/cyberframework
  - https://owasp.org/www-project-web-security-testing-guide/

---

# Reverse Engineering

> Recover program structure and behavior for authorized research or defense.

## Overview

Recover program structure and behavior for authorized research or defense. Use it only to answer a defined security question in an owned, local, CTF, synthetic, or explicitly authorized environment.

## Purpose

The purpose is to produce reproducible observations that inform remediation, detection, or risk decisions—not to obtain unauthorized access.

## Prerequisites

Understand the relevant protocols and authorization boundary. Prepare a disposable lab, a scope statement, timestamps, and a cleanup plan.

## How It Works

Define the input and expected evidence, perform the smallest safe action, record output and uncertainty, validate the observation, and map it to a control.

## Typical Security Workflow

1. Confirm ownership or written authorization and define scope.
2. Select an appropriate tool and conservative configuration.
3. Collect evidence without expanding scope.
4. Validate, report, remediate, and verify.

## Authorized Lab Usage

Use local services, intentionally vulnerable applications, synthetic artifacts, disposable VMs, or approved CTFs. Do not use unrelated public systems, accounts, or data.

## Tools

ghidra, radare2, cutter

## Technologies

Threat Modeling, Security Monitoring

## Related Vulnerabilities

Api Security, Authentication Weaknesses, Broken Access Control, Cloud Misconfiguration, Command Injection, Container Security

## Detection

Monitor the relevant application, network, endpoint, identity, cloud, or file telemetry. Detection should be tested against known-good and controlled events.

## Telemetry

Record timestamps, source and destination, process or request context, identity, configuration, and analyst actions as appropriate. Protect collected data.

## Defensive Controls

Endpoint Detection, Secure Logging

## Limitations

Coverage depends on scope, permissions, configuration, protocol support, data quality, and analyst interpretation. The technique cannot replace threat modeling or remediation verification.

## Common Mistakes

* Running without an approved scope or rate limit.
* Confusing a discovered surface with a confirmed vulnerability.
* Omitting timestamps, configuration, or evidence provenance.

## Related Labs

See the [safe lab hub](../../labs/README.md) and choose a lab that uses disposable or intentionally vulnerable assets.

## References

* [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
* [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
