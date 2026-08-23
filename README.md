# Universal Hacking Tools

> An open-source, safety-first cybersecurity knowledge platform for learning security concepts, tools, vulnerabilities, defensive techniques, digital forensics, privacy engineering, and secure development.

[![Documentation validation](https://github.com/gulshanverse/Universal-Hacking-Tools/actions/workflows/documentation.yml/badge.svg)](https://github.com/gulshanverse/Universal-Hacking-Tools/actions/workflows/documentation.yml)

## Mission

Universal Hacking Tools is designed to become a structured, searchable cybersecurity encyclopedia rather than a random list of commands. Each tool has an independent page, each vulnerability has a defensive knowledge page, and each lab is bounded to a disposable or explicitly authorized environment.

> **Legal and ethical boundary:** Use security tools only on systems, applications, networks, accounts, devices, or data that you own or have explicit permission to assess. Unauthorized scanning, exploitation, credential testing, interception, or access may be illegal. Dual-use material in this repository emphasizes concepts, safe labs, detection, mitigation, and responsible testing.

## Quick Navigation

| Area | Start here |
| --- | --- |
| Tools | [Tool encyclopedia](tools/README.md) |
| Vulnerabilities | [Vulnerability encyclopedia](vulnerabilities/README.md) |
| Labs | [Safe hands-on labs](labs/README.md) |
| Learning | [Learning paths](learning-paths/README.md) |
| Knowledge graph | [Connected taxonomy](knowledge/README.md) |
| Generated data | [JSON graph and indexes](generated/knowledge-graph.json) |
| Getting started | [First steps](docs/getting-started/README.md) |
| Contributing | [Contribution guide](CONTRIBUTING.md) |
| Safety | [Security policy](SECURITY.md) |
| Roadmap | [Project roadmap](ROADMAP.md) |

## What the Repository Contains

* **Tool pages:** source-backed, one-file-per-tool documentation covering purpose, metadata, safe usage, limitations, detection, mitigation, and references.
* **Concept documentation:** foundations for networking, web security, cloud, privacy, forensics, malware analysis, and secure development.
* **Vulnerability pages:** root cause, affected technology, impact, detection, mitigation, secure coding, safe labs, and taxonomy references.
* **Labs:** controlled exercises with setup, expected observations, defensive interpretation, and cleanup.
* **Learning paths:** staged progression for beginners, ethical hacking, penetration testing, bug bounty learning, blue team, SOC analysis, forensics, malware analysis, cloud security, and security engineering.
* **Knowledge graph:** typed concepts, techniques, technologies, defensive controls, and deterministic relationships to tools, vulnerabilities, labs, and learning paths.
* **Automation:** metadata validation, required-section checks, duplicate detection, internal-link checks, generated tool indexes, graph indexes, relationship validation, and artifact freshness checks.

## Tool Categories

Reconnaissance, OSINT, web security, network analysis, password security, wireless security, vulnerability management, reverse engineering, digital forensics, malware analysis, defensive security, secure development, cloud security, and container security.

## Learning Roadmap

Start with [Beginner Cybersecurity](learning-paths/beginner/README.md), then select a specialist path. Progress from concepts to controlled practice, evidence-based reporting, defensive interpretation, remediation, and verification. The project roadmap in [ROADMAP.md](ROADMAP.md) distinguishes implemented foundations from future work.

## Repository Statistics

The generated indexes report the current page counts. Run `python3 scripts/generate-index.py` after a content change so navigation stays synchronized.

## Automation

Run the following locally:

```bash
python3 scripts/validate_repository.py
python3 scripts/generate-index.py
python3 scripts/generate-index.py --check
python3 scripts/generate-knowledge.py
python3 scripts/validate-knowledge.py
python3 scripts/generate-knowledge.py --check
```

The GitHub Actions workflow runs the same consistency and relationship checks on pull requests and pushes.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md), copy the appropriate template, cite authoritative sources, keep examples inside authorized labs, and run validation before submitting a pull request. Quality and safety are more important than page count.

## Sources and Attribution

Tool pages link to official upstream repositories and documentation. General methodology links prefer OWASP, NIST, CISA, MITRE, RFCs, and vendor documentation. Tool licenses remain the responsibility of their upstream projects; this repository’s MIT license applies to repository-authored content, not to the tools it documents.
