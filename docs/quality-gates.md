# Publication Quality Gates

Automated checks determine whether a contribution is structurally valid and traceable. They do not replace human review of evidence, safety, scope, or educational value.

## Tools

A tool page is not publication-ready when its identity, description, source, license, platform, verification metadata, relationships, or safe-lab boundary is missing; when claims are fabricated; or when the page includes unsafe commands, real-world targeting, or unsupported benchmarks.

## Vulnerabilities

A vulnerability page is not publication-ready when its description, root cause, affected technology, impact, mitigation, source, or related-tool mapping is unsupported. A CWE or OWASP link is context, not automatic proof that a particular implementation is affected.

## Claims and Sources

Every important claim must have concrete evidence. Evidence must resolve to a source record or normalized source URL. Source records require a non-empty URL and stable metadata; malformed and duplicate records are reported for review rather than silently removed. Claim statuses, confidence values, source authority, and verification methods must use controlled vocabularies.

## Relationships and Prerequisites

Typed relationships must target existing entities, use approved relationship types, avoid self-references and duplicates, and have stronger justification when connecting vulnerabilities, techniques, tools, technologies, or defensive controls. Prerequisites must use `required`, `recommended`, or `helpful`, must resolve to an existing entity, and must not create cycles.

## Labs and Learning Paths

Labs must be local, synthetic, disposable, CTF-based, or explicitly authorized, with setup, observations, defensive interpretation, mitigation, and cleanup. Learning paths must expose a sensible progression through prerequisites, concepts, techniques, tools, vulnerabilities, labs, defensive knowledge, projects, and completion criteria.

## Human Review

The review lifecycle is **Draft → Automated Validation → Technical Review → Source Verification → Security Review → Documentation Review → Approved → Merged**. A `needs-review`, `unverified`, or `disputed` result is an honest outcome when evidence is incomplete; it is not an error to be hidden for the purpose of improving a score.
