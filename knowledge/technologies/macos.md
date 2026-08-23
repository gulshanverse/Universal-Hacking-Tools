---
id: macos
type: technology
name: macOS
status: needs-review
tools:
  - wireshark
  - ghidra
  - osquery

sources:
  - https://www.nist.gov/cyberframework
  - https://csrc.nist.gov/Projects/ssdf

---

# macOS

> A desktop operating system with application, identity, filesystem, and endpoint security controls.

## Overview

A desktop operating system with application, identity, filesystem, and endpoint security controls.

## Architecture

Document components, trust boundaries, identities, data flows, management planes, and exposed interfaces for the particular deployment. Avoid assuming that a product’s default configuration is secure.

## Security Model

Security depends on authenticated identities, authorization decisions, isolation, secure configuration, patching, protected data, and useful audit telemetry.

## Common Attack Surface

Review exposed services, administrative interfaces, dependencies, secrets, storage, network paths, update channels, and integrations.

## Common Vulnerabilities

Use the repository vulnerability pages for implementation-specific issues. Confirm preconditions and impact rather than applying a label without evidence.

## Security Controls

Apply least privilege, segmentation, secure configuration, encryption, protected logging, vulnerability management, and tested recovery appropriate to the deployment.

## Security Testing Considerations

Use a sandbox or authorized assessment, document scope, avoid sensitive data, and validate findings manually before reporting.

## Related Tools

wireshark, ghidra, osquery

## Related Techniques

Use the [technique index](../techniques/README.md) to select a method that matches the technology and authorized objective.

## Related Labs

Use a disposable local or cloud sandbox and follow the [lab hub](../../labs/README.md).

## Hardening

Start from a supported version and secure baseline, remove unnecessary exposure, restrict identities, enable audit logs, protect secrets, patch dependencies, and verify controls continuously.

## References

* [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
* [NIST Secure Software Development Framework](https://csrc.nist.gov/Projects/ssdf)
