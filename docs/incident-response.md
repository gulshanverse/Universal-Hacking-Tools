# Incident Response

This is an engineering response procedure, not a claim that a hosted alerting system or 24-hour response team is configured. Follow [SECURITY.md](../SECURITY.md) for the repository’s vulnerability-reporting path; do not place sensitive reports in public issues, discussions, or community proposal threads.

## Response lifecycle

| Phase | Required action | Privacy boundary |
| --- | --- | --- |
| Detect | Record the minimal event, time, service version, and affected capability. | Do not copy passwords, tokens, session/CSRF values, private notes, report contents, database URLs, or user-provided evidence into public logs. |
| Triage | Assess account, data, service, lab, Git-provider, or secret impact; freeze deployments for credible critical incidents. | Limit access to responders with a need to know. |
| Contain | Revoke credentials, disable optional provider use, suspend publication, or remove unsafe access paths as appropriate. | Preserve minimal audit evidence without publishing sensitive details. |
| Eradicate | Correct root cause, rotate affected credentials, review deployment/repository integrity, and validate the fix. | Use isolated test/staging data where possible. |
| Recover | Restore only through a reviewed recovery plan, verify health and critical flows, and monitor the chosen provider’s signals. | Never perform an untested restore over production. |
| Review | Record timeline, scope, corrective actions, and follow-up controls. | Publish only a sanitized summary when disclosure is appropriate. |

## Category playbooks

For **account compromise**, revoke sessions, reset credentials through a verified channel, inspect minimal account/audit metadata, and verify owner scoping. For a **secret leak**, freeze deployment, revoke and replace the affected secret, invalidate sessions when session/CSRF secrets rotate, audit trusted contexts, and only then resume. For **database compromise**, isolate connectivity, rotate database credentials, preserve evidence, assess exposure, and restore only after a reviewed decision.

For a **Git-provider credential concern**, revoke the credential, disable the optional provider adapter, audit proposed handoffs/branches/pull requests, and use manual review until least-privilege access is restored. For a **malicious contribution**, freeze publication, inspect controlled proposal and audit records, revert Git changes if a reviewed canonical change was accepted, and apply moderation according to [moderation](moderation.md). For **lab abuse**, disable the affected local-fixture capability, preserve minimal evidence, and confirm that no remote system was targeted. For a **service outage**, use health/readiness/liveness evidence, preserve generated public-read availability where possible, and avoid queuing private writes.

## External response gap

Pager, security contact roster, provider support channel, log sink, and legal-notification obligations are **blocked — external prerequisite unavailable**. The deployment operator must record them before public launch.
