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
| Labs | [Safe hands-on labs](labs/README.md) · [Architecture](docs/lab-architecture.md) · [Safety](docs/lab-safety.md) |
| Learning | [Learning paths](learning-paths/README.md) |
| Knowledge graph | [Connected taxonomy](knowledge/README.md) |
| Generated data | [JSON graph and indexes](generated/knowledge-graph.json) |
| Content health | [Completeness report](generated/content-completeness.json) · [Verification report](generated/verification-report.json) · [Review queue](generated/review-queue.json) · [Lab health](generated/lab-health.json) |
| Trust and evidence | [Trust report](generated/trust-report.json) · [Source catalog](generated/source-catalog.json) · [Claim report](generated/claim-report.json) · [Verification history](verification-history/README.md) |
| Phase 7 platform | [API contract](docs/api.md) · [Web platform](docs/web-platform.md) · [Deployment notes](docs/deployment.md) |
| Getting started | [First steps](docs/getting-started/README.md) |
| Contributing | [Contribution guide](CONTRIBUTING.md) |
| Safety | [Security policy](SECURITY.md) |
| Roadmap | [Project roadmap](ROADMAP.md) |

## What the Repository Contains

* **Tool pages:** source-backed, one-file-per-tool documentation covering purpose, metadata, safe usage, limitations, detection, mitigation, and references.
* **Concept documentation:** foundations for networking, web security, cloud, privacy, forensics, malware analysis, and secure development.
* **Vulnerability pages:** root cause, affected technology, impact, detection, mitigation, secure coding, safe labs, and taxonomy references.
* **Labs:** controlled exercises with setup, expected observations, defensive interpretation, cleanup, and a Phase 6 classification as documentation-only, guided, or executable. Six safe local-fixture reference labs are executable through the CLI.
* **Learning paths:** staged progression for beginners, ethical hacking, penetration testing, bug bounty learning, blue team, SOC analysis, forensics, malware analysis, cloud security, and security engineering.
* **Knowledge graph:** typed concepts, techniques, technologies, defensive controls, and deterministic relationships to tools, vulnerabilities, labs, and learning paths.
* **Phase 7 API and web client:** a versioned read-only FastAPI adapter over generated contracts, a responsive API-backed Next.js knowledge archive, OpenAPI contract checks, and browser validation. The public layer introduces no database, accounts, telemetry, external API dependency, or alternate content source.
* **Automation:** metadata validation, required-section checks, duplicate detection, internal-link checks, generated tool indexes, graph indexes, prerequisite and relationship validation, deterministic search artifacts, content-completeness reports, verification reports, source normalization, claim traceability, trust reports, review queues, Phase 6 lab safety/catalog/health reports, Phase 7 API/web checks, and artifact freshness checks.

## Cybersecurity Knowledge Graph and Intelligence

The repository now includes a deterministic [knowledge graph](knowledge/README.md), a local [Search and Discovery Engine](search/README.md), [knowledge health reporting](generated/knowledge-health.json), a per-entity [content-completeness report](generated/content-completeness.json), a [verification report](generated/verification-report.json), normalized [source records](generated/source-catalog.json), selective [evidence-backed claims](generated/claim-report.json), transparent [trust reporting](generated/trust-report.json), a prioritized [review queue](generated/review-queue.json), the Phase 6 [local lab framework](labs/README.md), and a Phase 7 [versioned API and web platform](docs/api.md). The API and web client consume generated contracts and existing deterministic engines without replacing Markdown/YAML as the source of truth.

Try it locally with `python3 scripts/search.py nmap`, `python3 scripts/search.py --explore nmap --depth 2`, `python3 scripts/search.py --health`, `python3 scripts/lab.py list`, `python3 scripts/lab.py --format json create dns-resolution-inventory --dry-run`, `make api`, and `cd apps/web && pnpm dev`.

## Tool Categories

Reconnaissance, OSINT, web security, network analysis, password security, wireless security, vulnerability management, reverse engineering, digital forensics, malware analysis, defensive security, secure development, cloud security, and container security.

## Learning Roadmap

Start with [Beginner Cybersecurity](learning-paths/beginner/README.md), then select a specialist path. Progress from concepts to controlled practice, evidence-based reporting, defensive interpretation, remediation, and verification. The project roadmap in [ROADMAP.md](ROADMAP.md) distinguishes implemented foundations from future work.

## Repository Statistics

The generated indexes report the current page counts. The current Phase 5 baseline is 70 tools, 40 vulnerabilities, 61 concepts, 34 techniques, 35 technologies, 30 defensive controls, 22 labs, 15 learning paths, and 307 total typed entities. Phase 6 adds six executable local-fixture definitions without expanding the knowledge-entity inventory; Phase 7 adds contract consumers rather than mass content expansion.
The deterministic health score is reported in [`generated/knowledge-health.json`](generated/knowledge-health.json); it is not adjusted to improve appearance. Run `python3 scripts/generate-index.py` after a content change so navigation stays synchronized.

## Automation

Run the following locally:

```bash
python3 scripts/validate_repository.py
python3 scripts/generate-index.py
python3 scripts/generate-index.py --check
python3 scripts/generate-knowledge.py
python3 scripts/generate-lab-reports.py
python3 scripts/validate-knowledge.py
python3 scripts/generate-knowledge.py --check
python3 scripts/generate-search.py
python3 scripts/generate-trust-reports.py
python3 scripts/generate-quality-reports.py
python3 scripts/validate-labs.py
python3 scripts/validate-schemas.py
python3 scripts/validate-quality.py
python3 scripts/validate-trust.py
python3 scripts/generate-search.py --check
python3 scripts/generate-trust-reports.py --check
python3 scripts/generate-quality-reports.py --check
python3 scripts/generate-lab-reports.py --check
python3 scripts/search.py nmap --format json
python3 scripts/search.py --trust
python3 scripts/search.py --review-queue
python3 scripts/lab.py list
python3 scripts/lab.py validate
python3 scripts/lab.py --format json create dns-resolution-inventory --dry-run
python3 -m unittest discover -s tests -v
PYTHONPATH=apps/api:. python3 -m unittest discover -s apps/api/tests -v
python3 apps/api/scripts/export_openapi.py
PYTHONPATH=apps/api:. python3 apps/api/scripts/check_openapi.py
cd apps/web && pnpm test && pnpm typecheck && NODE_ENV=production pnpm build
```

The GitHub Actions workflow runs the same consistency, relationship, prerequisite, search-artifact, content-quality, contract, and test checks on pull requests and pushes.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md), copy the appropriate template, cite authoritative sources, keep examples inside authorized labs, and run validation before submitting a pull request. Quality and safety are more important than page count.

## Sources and Attribution

Tool pages link to official upstream repositories and documentation. General methodology links prefer OWASP, NIST, CISA, MITRE, RFCs, and vendor documentation. Tool licenses remain the responsibility of their upstream projects; this repository’s MIT license applies to repository-authored content, not to the tools it documents.
