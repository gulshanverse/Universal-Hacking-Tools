---
id: network-security
type: learning-path
name: Network Security
status: needs-review
prerequisites:
  - networking
  - threat-modeling
concepts:
  - networking
  - tcp-ip
  - ports
  - services
  - firewalls
tools:
  - nmap
  - wireshark
  - zeek
techniques:
  - security-testing
labs:
  - localhost-service-inventory
  - packet-capture-fundamentals
technologies:
  - linux
---

# Network Security

> A staged, safety-first learning path.

## Goal

Build a defensible understanding of network security through concepts, controlled practice, evidence, detection, mitigation, and verification.

## Prerequisites

Start with the linked prerequisites and use only owned, synthetic, local, CTF, or explicitly authorized environments.

## Beginner Stage

Study the concepts first, learn the terminology, and complete the first safe lab with a written scope and cleanup plan.

## Intermediate Stage

Use the listed tools against a disposable fixture, record configuration and evidence, and explain false positives, false negatives, limitations, and defensive telemetry.

## Advanced Stage

Design a repeatable assessment or detection exercise, map findings to controls, and verify remediation without expanding beyond authorization.

## Concepts

- [Networking](../../knowledge/concepts/networking.md)
- [Tcp Ip](../../knowledge/concepts/tcp-ip.md)
- [Ports](../../knowledge/concepts/ports.md)
- [Services](../../knowledge/concepts/services.md)
- [Firewalls](../../knowledge/concepts/firewalls.md)

## Techniques

- [Security Testing](../../knowledge/techniques/security-testing.md)

## Tools

- [Nmap](../../tools/reconnaissance/nmap.md)
- [Wireshark](../../tools/network-analysis/wireshark.md)
- [Zeek](../../tools/network-analysis/zeek.md)

## Vulnerabilities

Use the [vulnerability encyclopedia](../../vulnerabilities/README.md) to choose implementation-specific classes rather than assuming a finding.

## Labs

- Localhost Service Inventory
- Packet Capture Fundamentals

## Defensive Knowledge

Connect each exercise to logging, least privilege, secure configuration, segmentation, and remediation verification.

## Suggested Projects

Create a small, disposable project that documents scope, assumptions, evidence, limitations, controls, cleanup, and completion criteria. Never publish secrets, personal data, malicious payloads, or results from uninvolved systems.

## Completion Criteria

You can explain the concepts, select an authorized method, preserve evidence, communicate uncertainty, recommend mitigation, and verify a fix.
