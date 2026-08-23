# Phase 6 Lab Authoring Guide

Executable labs require stronger review than ordinary documentation. Start with a narrowly scoped learning objective, decide whether the existing lab should remain `documentation-only`, become `guided`, or become `executable`, and only then author a local synthetic definition.

## Authoring sequence

1. Define the learning objective and completion criteria.
2. Declare genuine typed prerequisites.
3. Select a committed synthetic fixture and a local-only target.
4. Declare bounded resources, timeout, one-instance limit, and safety invariants.
5. Add a small task set using only actions from the closed allowlist.
6. Define the evidence record and deterministic assessment criterion for each task.
7. Map the lab to existing concepts, techniques, tools, vulnerabilities, defensive controls, and learning paths.
8. Document observations, detection, mitigation, and cleanup on the Markdown page.
9. Run lab schema and safety validation, lifecycle tests, regression tests, and generated-artifact checks.
10. Submit the executable lab for technical, source, security, and documentation review.

## Definition format

Files under `labs/definitions/` use JSON-compatible YAML. This is a dependency-free YAML 1.2 subset: it keeps the repository’s structured YAML model while allowing the standard library to parse definitions deterministically. Required fields are documented by [`labs/schemas/lab.schema.json`](../labs/schemas/lab.schema.json).

A task must name a target, an allowlisted action, and an evidence record. It must not contain a shell command, a command template, a URL, a host path, credentials, or an instruction to contact a real system. A fixture path must remain below `labs/fixtures/` and end in `.json`.

## Classification

Use `executable` only when the exercise can be safely represented by the current local-fixture runner. Use `guided` when a learner needs manual local or explicitly authorized interpretation that the runner does not model. Use `documentation-only` when the content is conceptual, sensitive, or not yet suitable for a reproducible fixture. Classification is not a verification claim.

## Review

Run `python3 scripts/validate-labs.py` before opening a pull request. Automated results identify structural and safety defects, but they do not establish that a security claim is factually correct. Human reviewers must inspect evidence, safety boundaries, source quality, scope, and whether the educational framing explains detection and mitigation as well as the offensive concept.
