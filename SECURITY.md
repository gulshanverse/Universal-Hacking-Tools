# Security Policy

This repository is educational and must not contain secrets, malware, destructive payloads, credential theft workflows, persistence mechanisms, evasion instructions, or instructions to exploit uninvolved systems. All examples must be limited to local labs, CTFs, owned infrastructure, synthetic data, or written authorized assessments.

## Reporting a security concern

Do not open a public issue, public proposal, review comment, or profile post with sensitive details. Use the private security-report path in the authenticated community workspace when it is available, or contact the maintainers through the channel listed in the project profile. Include only the minimum information needed to reproduce and assess the concern. Do not include live credentials, personal data, private keys, customer data, or targeting instructions.

Private reports are visible only to authorized application roles and are not knowledge-editing mechanisms. Report resolution does not publish details, change repository content, or promise a response time. For non-sensitive content corrections, use a focused issue or a controlled proposal with authoritative sources.

## Handling and disclosure

Maintainers should acknowledge, triage, and resolve sensitive reports privately; publication timing and remediation details are a human governance decision. Do not disclose a report to public issue threads without reporter consent and an explicit safety review. If an accidental secret is committed, rotate and revoke it outside the repository before any public discussion, then remove it through the project’s normal [incident response](docs/incident-response.md). The production [secret-management runbook](docs/production-secrets.md) documents required server-side handling and rotation effects; neither document claims a configured production secret store or emergency contact roster.
