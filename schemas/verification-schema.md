# Verification Schema

Phase 5 verification metadata records the strength and limits of the available evidence. It does not certify an entity merely because a page has been reviewed.

```yaml
verification:
  status: needs-review
  confidence: low
  last_verified: 2026-08-23
  verification_method: manual-review
  reviewer: repository-audit
  review_notes: Explain what was checked and what remains uncertain.
```

| Field | Allowed values or format | Meaning |
| --- | --- | --- |
| `status` | `verified`, `partially-verified`, `needs-review`, `unverified`, `deprecated` | Current evidence state. `deprecated` requires reliable evidence of project or concept deprecation. |
| `confidence` | `high`, `medium`, `low`, `unknown` | Confidence in the verified claims, not a popularity or risk score. |
| `last_verified` | ISO date or empty | Date of the most recent controlled review. |
| `verification_method` | Controlled values below | How the review was performed. |
| `reviewer` | Contributor handle or role | Who or what role performed the review; do not store sensitive personal information. |
| `review_notes` | Short prose | Scope, evidence limits, changed facts, and follow-up work. |

Allowed verification methods are `official-documentation`, `official-repository`, `official-website`, `maintainer-documentation`, `security-standard`, `vendor-documentation`, `primary-research`, `secondary-research`, `manual-review`, and `cross-source-review`. Arbitrary values are invalid.

A high-confidence status requires direct authoritative evidence or multiple strong sources for the particular claim. Source count alone is insufficient. Older documentation, partial evidence, or unresolved mappings should remain medium, low, or unknown.
