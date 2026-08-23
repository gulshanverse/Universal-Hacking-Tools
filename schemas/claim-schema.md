# Claim Schema

Important factual assertions may be represented as evidence-backed claims. Claims are selective; contributors should not copy a claim block into every page without a concrete reason.

```yaml
claims:
  - id: tool-purpose
    statement: "The documented purpose is supported by the official documentation."
    evidence:
      - source: official-documentation
        note: "The source describes the relevant functionality."
    status: partially-verified
    confidence: medium
```

| Field | Requirement |
| --- | --- |
| `id` | Unique within the entity; use a stable lowercase hyphenated identifier. |
| `statement` | One specific, reviewable factual assertion. Avoid marketing or unsupported superlatives. |
| `evidence` | One or more evidence records. Every record must resolve to a source ID or controlled source reference. |
| `status` | `verified`, `partially-verified`, `needs-review`, `disputed`, or `deprecated`. Disputed claims are retained and surfaced for review. |
| `confidence` | `high`, `medium`, `low`, or `unknown`, justified by the evidence. |

The traceability chain is **entity → claim → evidence → source → verification**. A claim without evidence, evidence without a valid source, duplicate claim IDs, invalid statuses, or invalid confidence values fails validation. The repository does not infer truth from a claim’s wording.
