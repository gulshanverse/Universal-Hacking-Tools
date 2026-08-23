# Content Review Checklist

Use this checklist for every new or materially revised tool, vulnerability, concept, technique, technology, defensive-control, lab, or learning-path page.

## Accuracy and Sources

- [ ] Name and terminology are verified.
- [ ] Description is specific, factual, and free of marketing claims.
- [ ] Official repository, website, documentation, or authoritative standard was checked.
- [ ] License and platform claims are verified where applicable.
- [ ] References are real, relevant, and not fabricated.
- [ ] Verification status, confidence, method, reviewer role, and date are honest.
- [ ] Verification history records the review scope and unresolved follow-up without sensitive personal information.
- [ ] Source records include stable IDs, titles, URLs, access dates where known, authority, and notes.
- [ ] Duplicate or suspicious sources are reported rather than silently deleted.

## Metadata and Relationships

- [ ] Required YAML fields are complete.
- [ ] Prerequisites are genuine and use canonical IDs.
- [ ] Relationships are justified and use the correct entity type.
- [ ] Related labs are safe, disposable, synthetic, local, CTF-based, or explicitly authorized.
- [ ] No unnecessary relationship was added only to increase graph density.
- [ ] Reverse relationships and search metadata regenerate correctly.
- [ ] Important claims have evidence records that resolve to source records.
- [ ] Claim status and confidence are justified; disputed claims are retained and surfaced.
- [ ] Prerequisites are classified as required, recommended, or helpful rather than all being marked required.

## Safety and Scope

- [ ] Security boundaries are explicit.
- [ ] No credential-theft workflow is included.
- [ ] No malware creation, ransomware, persistence, destructive action, evasion, data theft, or unauthorized access guidance is included.
- [ ] Examples do not target uninvolved public systems.
- [ ] Sensitive data collection is minimized and protected.
- [ ] No secrets, personal data, debug output, or temporary artifacts are committed.

## Technical Quality

- [ ] Required documentation sections are present.
- [ ] Commands, if any, are verified and limited to the authorized lab scope.
- [ ] Limitations, false positives, false negatives, and assumptions are documented.
- [ ] Detection, mitigation, cleanup, and remediation verification are addressed where applicable.
- [ ] Internal links resolve.
- [ ] Generated indexes, health, verification, source, claim, prerequisite, trust, and review reports are current.

## Review Lifecycle

A normal contribution moves through **Draft → Technical Review → Source Verification → Security Review → Documentation Review → Approved → Merged**. Reviewers may return a page to an earlier stage when a source, scope, relationship, or safety issue is found.
