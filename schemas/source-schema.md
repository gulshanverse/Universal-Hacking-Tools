# Source Record and Authority Model

Source records are evidence pointers, not automatic proof of every claim. Contributors must select a source that supports the specific assertion under review.

```yaml
sources:
  - id: official-documentation
    title: Official documentation
    type: official-documentation
    url: https://example.invalid/docs
    accessed: 2026-08-23
    authority: high
    notes: Identify the claim or metadata supported by this source.
```

## Source hierarchy

For tools, prefer official documentation, the official repository, the official website, maintainer documentation, vendor documentation, reputable security research, academic research, and then secondary sources. For vulnerabilities, prefer NIST, OWASP, MITRE, CISA, relevant RFCs, vendor advisories, primary research, and reputable secondary research.

## Authority

`high` is reserved for direct authoritative documentation or standards that support the relevant claim. `medium` is appropriate for reliable but incomplete vendor, maintainer, or security documentation. `low` is appropriate for secondary, old, partial, or otherwise limited evidence. Unknown authority must remain `unknown` until reviewed. A repository-authored URL may use `type: maintainer-documentation` and `authority: medium` when it documents local exercise or path structure; it must not be presented as independent evidence for external security facts.

## Normalization and review

The Phase 5 source catalog normalizes scheme and host case, removes trailing slashes, and removes URL fragments while preserving query parameters. It reports duplicate normalized URLs, duplicate titles, empty URLs, and malformed URLs without deleting them. A reviewer decides whether two records are genuinely the same source or intentionally distinct representations.
