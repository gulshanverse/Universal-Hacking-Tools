# Contributing

Thank you for improving this educational cybersecurity knowledge base. Contributions should be accurate, reproducible, respectful, and clearly bounded to owned or explicitly authorized environments.

## Adding a Tool

Copy [`templates/tool-template.md`](templates/tool-template.md) into the appropriate category, use a lowercase hyphenated filename, complete every front-matter field, and cite the official repository, website, and documentation. Do not invent versions, capabilities, commands, licenses, or benchmarks. Run `python3 scripts/validate_repository.py` and `python3 scripts/generate-index.py` before opening a pull request.

## Adding a Vulnerability

Copy [`templates/vulnerability-template.md`](templates/vulnerability-template.md), describe the root cause and defensive impact, link to CWE or OWASP where appropriate, and use a local lab. Do not include credential theft, malware, persistence, evasion, destructive actions, or exploitation instructions for uninvolved systems.

## Adding a Lab

Copy [`templates/lab-template.md`](templates/lab-template.md). State the objective, prerequisites, environment, setup, expected observations, defensive interpretation, cleanup, and further learning. Disposable local environments and intentionally vulnerable applications are preferred.

## Style and Review

Use clear technical prose, relative links for repository content, authoritative references, and explicit uncertainty. Reviewers check accuracy, scope, metadata, links, safety boundaries, and whether the page adds educational value without repetitive filler.

## Commit and Pull Request Guidance

Use focused commits such as `docs: add tool page for ...` or `ci: improve metadata validation`. Complete the pull-request template, explain sources and testing, and disclose any limitations. Never commit secrets, personal data, malware, exploit payloads for real targets, or material that facilitates unauthorized access.
