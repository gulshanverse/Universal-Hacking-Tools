# Contributing

Thank you for improving this educational cybersecurity knowledge base. Contributions should be accurate, reproducible, respectful, and clearly bounded to owned or explicitly authorized environments.

## Adding a Tool

Copy [`templates/tool-template.md`](templates/tool-template.md) into the appropriate category, use a lowercase hyphenated filename, complete every front-matter field, and cite the official repository, website, and documentation. Do not invent versions, capabilities, commands, licenses, or benchmarks. Run `python3 scripts/validate_repository.py`, `python3 scripts/validate-knowledge.py`, `python3 scripts/generate-index.py`, `python3 scripts/generate-knowledge.py`, `python3 scripts/generate-search.py`, `python3 scripts/generate-quality-reports.py`, `python3 scripts/validate-schemas.py`, `python3 scripts/validate-quality.py`, `python3 scripts/generate-search.py --check`, `python3 scripts/generate-quality-reports.py --check`, and `python3 -m unittest discover -s tests -v` before opening a pull request.

## Adding a Vulnerability

Copy [`templates/vulnerability-template.md`](templates/vulnerability-template.md), describe the root cause and defensive impact, link to CWE or OWASP where appropriate, and use a local lab. Do not include credential theft, malware, persistence, evasion, destructive actions, or exploitation instructions for uninvolved systems.

## Adding a Lab

Copy [`templates/lab-template.md`](templates/lab-template.md). State the objective, prerequisites, environment, setup, expected observations, defensive interpretation, cleanup, and further learning. Disposable local environments and intentionally vulnerable applications are preferred.

## Relationships and Verification

Phase 2 uses Markdown and YAML as the source of truth for a future knowledge graph. Tools should declare `concepts`, `techniques`, `technologies`, `related_tools`, `related_vulnerabilities`, `related_labs`, `defensive_controls`, `verification`, and `sources`. Vulnerability, lab, and learning-path pages should declare their corresponding typed relationships. Use repository slugs, not display names, and mark uncertain mappings `needs-review` rather than guessing.

After editing relationship metadata, add `prerequisites` only when the dependency is genuine and use canonical IDs. Prefer structured records such as `target: tcp-ip` with `type: required`, `recommended`, or `helpful`; do not classify every background topic as required. Run the graph and search generators, then `python3 scripts/generate-quality-reports.py` and `python3 scripts/generate-trust-reports.py`. Generated JSON under `generated/` is deterministic and must not be manually edited. The graph validator rejects unknown entity references, invalid relationship types, duplicate relationships, and inappropriate self-references. Search results are offline and deterministic; the CLI never executes commands, makes network requests, or evaluates content as code.

## Review Lifecycle

Contributions move through **Draft → Technical Review → Source Verification → Security Review → Documentation Review → Approved → Merged**. Technical Review checks structure, terminology, scope, and implementation claims. Source Verification checks official repositories, standards, licenses, platforms, and dates. Security Review checks authorization boundaries, dual-use framing, lab isolation, and absence of prohibited content. Documentation Review checks links, cross-links, prerequisites, metadata, readability, and generated artifacts. A reviewer may return a contribution to an earlier stage rather than silently accepting uncertainty.

Use [`docs/content-review-checklist.md`](docs/content-review-checklist.md), inspect [`generated/content-completeness.json`](generated/content-completeness.json), [`generated/verification-report.json`](generated/verification-report.json), [`generated/source-catalog.json`](generated/source-catalog.json), [`generated/claim-report.json`](generated/claim-report.json), [`generated/prerequisite-report.json`](generated/prerequisite-report.json), [`generated/trust-report.json`](generated/trust-report.json), and [`generated/review-queue.json`](generated/review-queue.json). Record unresolved issues honestly as `needs-review`, `unverified`, or `disputed`; never upgrade status to improve a metric.

## Evidence and Verification

Use the controlled fields documented in [`schemas/verification-schema.md`](schemas/verification-schema.md) and source records documented in [`schemas/source-schema.md`](schemas/source-schema.md). Important factual assertions may be added selectively to [`evidence/claims.json`](evidence/claims.json), following [`schemas/claim-schema.md`](schemas/claim-schema.md). Every claim evidence record must resolve to a source URL in the normalized source catalog. Keep verification history in [`verification-history/`](verification-history/), use contributor handles only when intentionally provided, and do not store sensitive personal information.

Automated validation detects malformed sources, duplicate normalized URLs, duplicate claim IDs, missing evidence, invalid claim statuses or confidence, broken traceability, prerequisite cycles, invalid relationship evidence, and stale generated artifacts. These checks support human review; they do not replace source verification, security review, or documentation review.

Before opening a pull request, run `python3 scripts/validate_repository.py`, `python3 scripts/validate-knowledge.py`, `python3 scripts/validate-quality.py`, `python3 scripts/validate-trust.py`, `python3 scripts/validate-labs.py`, `python3 scripts/validate-schemas.py`, `python3 scripts/check-links.py`, `python3 scripts/generate-index.py --check`, `python3 scripts/generate-knowledge.py --check`, `python3 scripts/generate-search.py --check`, `python3 scripts/generate-trust-reports.py --check`, `python3 scripts/generate-quality-reports.py --check`, `python3 scripts/generate-lab-reports.py --check`, and `python3 -m unittest discover -s tests -v`.
Automated checks are gates for structural quality, not a substitute for human review of evidence, safety, scope, or relationships.

## Phase 7–10 API, Web, Graph, Private-State, and Community Platform

The API and web client consume generated contracts; they do not create a second cybersecurity knowledge source or authorize browser-side content editing. Keep API changes additive within `/api/v1`, update the committed `apps/api/openapi.json` through `python3 apps/api/scripts/export_openapi.py`, and run its freshness check. PostgreSQL changes are limited to owner-scoped private application state and require an Alembic migration, threat-model review, IDOR and deletion-cascade tests, and rollback documentation. Do not add content tables, remote data fetches, telemetry, public profiles, comments, generic command execution, shell endpoints, target-selection fields, uploads, or browser access to repository files.

Phase 9 graph changes must reuse `IndexLoader` and the generated graph rather than adding a Markdown parser, graph database, LLM, embedding, vector index, or web knowledge-mutation route. Graph traversals must reject depth above 4, node limits above 100, edge limits above 200, and path lengths above 25 before traversal. Relationship explanations require controlled templates or an explicit review-needed result. Orphan suggestions remain read-only, use deterministic metadata overlap only, and must be labeled **SUGGESTION ONLY — REQUIRES HUMAN REVIEW**. Regenerate `generated/graph-health.json` with `python3 scripts/generate-graph-intelligence.py`; do not edit it manually.

Web changes must preserve the Signal Archive accessibility and safety model: semantic landmarks, skip-link focus, explicit text verification status, keyboard-reachable search, bounded relationship rendering with a list alternative, responsive layouts, and reduced-motion support. The graph SVG is supplementary: every core action needs a keyboard-accessible structured list/table, live status announcement, and no user-controlled SVG/HTML injection. Private graph overlays may show only the authenticated caller's progress labels and may not place private state in public URLs or shared caches. Private web changes must use cookie-authenticated sessions and CSRF-protected mutations, must not place account tokens or private notes in browser storage, and must render notes as plain text. The lab workspace may call only published lifecycle and declared task/evidence endpoints for already validated local fixtures; only minimal authenticated summaries may be retained, never raw evidence.

Before opening a Phase 7–10 pull request, run `python3 scripts/generate-graph-intelligence.py --check`, `python3 -m unittest discover -s tests -v`, `PYTHONPATH=apps/api:. python3 -m unittest discover -s apps/api/tests -v`, exercise `alembic upgrade head`, `alembic downgrade base`, and `alembic upgrade head` against a disposable database, run `python3 apps/api/scripts/export_openapi.py`, `PYTHONPATH=apps/api:. python3 apps/api/scripts/check_openapi.py`, `cd apps/web && pnpm test`, `pnpm typecheck`, and `NODE_ENV=production pnpm build`. Run the browser suite only with a locally running API and web server plus disposable database and lab-state directories. Automated API, graph, web, and browser checks are still not a substitute for human security, privacy, accessibility, and source review.

## Phase 10 Community Collaboration

The application’s community workspace is a controlled intake and review aid, not a public editor. A proposal is always **PROPOSED CONTENT — NOT CANONICAL KNOWLEDGE**. Use only the published contribution templates and plain-text fields. Do not submit raw exploit instructions, target details, credentials, private data, executable payloads, uploads, arbitrary Markdown or HTML, or public security-report details. The service validates bounded fields and generated-knowledge references, but validation is not publication or fact verification.

Proposal authors may create, revise, submit, or withdraw only their own private proposal records. Reviewer, maintainer, and administrator permissions are server-enforced; reputation is deterministic recognition and never grants a role. Reviewers must disclose or avoid conflicts, must not review their own contribution, and must write specific plain-text rationale. A maintainer’s approval does not modify Git, generated JSON, Markdown/YAML, labs, or history. A server-side Git-provider handoff may be recorded only after approval. When no provider is configured, the result is deliberately failed and contributors must use the documented manual pull-request workflow; never represent a failed or queued handoff as a created pull request.

Use [the contributor quick start](docs/contributor-quickstart.md), [workflow](docs/contribution-workflow.md), [review checklist](docs/content-review-checklist.md), [reviewer guide](docs/reviewer-guide.md), and [maintainer guide](docs/maintainer-guide.md). Keep repository edits and generated artifacts in a conventional pull request. Run repository validation and obtain human maintainer review before any canonical knowledge change.

## Phase 6 Executable Labs

Classify every existing lab as `documentation-only`, `guided`, or `executable`; do not convert all labs automatically. An executable lab must link its definition through flat Markdown front matter such as `execution_mode: executable` and `definition: definitions/example.yaml`. Keep the learner-facing explanation in Markdown and place machine-readable tasks, targets, evidence, assessment, cleanup, safety, and learning mappings in `labs/definitions/`.

Use JSON-compatible YAML definitions so the standard library can validate them without adding a dependency. Fixtures must be committed synthetic JSON under `labs/fixtures/` and must not contain real credentials, personal data, malware, persistence, production secrets, arbitrary host paths, or real-world targets. Definitions must require local-fixture execution, dedicated ephemeral isolation, no internet, no host networking, no privileged execution, no host mounts, bounded resources, a finite timeout, and one active instance per lab.

Tasks may invoke only the closed allowlist of fixture-inspection actions. Do not add shell strings, arbitrary subprocess execution, `eval`, `exec`, dynamic downloads, remote images, or unrestricted commands. Evidence is local and ephemeral, and deterministic assessment must use explicit rubric criteria; a successful fixture run never upgrades content verification status.

Before proposing an executable lab, run `python3 scripts/validate-labs.py`, exercise `python3 scripts/lab.py --format json create <lab-id> --dry-run`, test create/start/run/evidence/assess/stop/reset/destroy and invalid transitions, regenerate `lab-catalog.json`, `lab-health.json`, and `lab-report.json`, and inspect the safety and threat-model documentation. Executable labs require technical, source, security, and documentation review; automated validation does not replace human review.

## Style and Review

Use clear technical prose, relative links for repository content, authoritative references, and explicit uncertainty. Reviewers check accuracy, scope, metadata, links, safety boundaries, and whether the page adds educational value without repetitive filler. For tools, cite the official repository, official website, and official documentation when verified, and record the verification date.

## Commit and Pull Request Guidance

Use focused commits such as `docs: add tool page for ...` or `ci: improve metadata validation`. Complete the pull-request template, explain sources and testing, and disclose any limitations. Never commit secrets, personal data, malware, exploit payloads for real targets, or material that facilitates unauthorized access.
