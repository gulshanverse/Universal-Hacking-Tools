---
id: containers
type: concept
name: Containers
status: needs-review
prerequisites:
  - linux
  - processes
sources:
  - https://opencontainers.org/
  - https://kubernetes.io/docs/concepts/overview/what-is-kubernetes/
---

# Containers

> A packaging and isolation model for applications and their dependencies, with security boundaries defined by the runtime and configuration.

## Overview

Containers improve portability and deployment consistency, but they are not a universal security boundary. Image provenance, privileges, namespaces, capabilities, mounted data, network policy, runtime configuration, and host trust all matter.

## Security Relevance

Review containers as part of a larger workload and supply-chain system. A secure image can still be deployed with excessive privileges, exposed interfaces, weak identity, or insufficient logging.

## Common Security Issues

Common issues include untrusted images, embedded secrets, excessive Linux capabilities, privileged execution, host-path exposure, weak registry controls, missing patching, and broad service-account permissions.

## Defensive Perspective

Use approved image sources, dependency review, signed artifacts where appropriate, minimal images, least privilege, network segmentation, runtime monitoring, and tested recovery. Keep credentials outside images and protect build logs.

## Related Technologies

* [Docker](../technologies/docker.md)
* [Kubernetes](../technologies/kubernetes.md)
* [Linux](../technologies/linux.md)

## Related Techniques

* [Container Security Scanning](../techniques/container-security-scanning.md)
* [IaC Scanning](../techniques/iac-scanning.md)

## Related Defensive Controls

* [Secure Configuration](../defensive-controls/secure-configuration.md)
* [Least Privilege](../defensive-controls/least-privilege.md)
* [Supply-Chain Controls](../defensive-controls/supply-chain-controls.md)

## References

* [Open Container Initiative](https://opencontainers.org/)
* [Kubernetes Documentation](https://kubernetes.io/docs/concepts/overview/what-is-kubernetes/)
* [NIST Application Container Security Guide](https://csrc.nist.gov/publications/detail/sp/800-190/final)
