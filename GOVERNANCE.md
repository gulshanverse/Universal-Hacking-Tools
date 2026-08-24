# Governance

Universal Hacking Tools is maintained through reviewed, source-backed contributions. Maintainers protect the project’s educational purpose, safety boundary, privacy expectations, and long-term consistency. Changes that affect content, taxonomy, generated artifacts, database migrations, or automation must state their impact and validation evidence. Decisions are made by consensus where practical; maintainers may defer, revise, or reject material that is inaccurate, unsafe, duplicative, legally ambiguous, or not useful to learners.

## Authority boundary

Markdown and YAML committed to Git, together with their deterministic generated JSON artifacts, are the only authoritative cybersecurity knowledge sources. The Phase 10 community application stores private profiles, proposals, versions, review records, reports, reputation events, and audit events as application state only. No role, approval, application record, or provider-handoff status can directly edit canonical knowledge, generated artifacts, Git history, or labs.

| Role | May do | May not do |
| --- | --- | --- |
| Contributor | Create a profile, draft controlled proposals, revise or submit own proposals, and file private reports | Grant roles, review own work, publish knowledge, or alter Git through the web app |
| Reviewer | Read the restricted queue, comment, request changes, recommend approval, and reject with rationale | Review own work, grant roles, merge, publish, or change canonical knowledge |
| Maintainer | Perform reviewer functions, assign an eligible reviewer, approve a reviewed proposal, and request a controlled server-side handoff | Treat a handoff as success unless the provider confirms it, or bypass canonical PR review and CI |
| Administrator | Moderate application accounts, assign roles with an audit reason, and resolve private reports | Moderate their own account, expose sensitive reports, or alter canonical knowledge through application state |

## Review and conflicts

Every review decision must contain a specific plain-text reason. Reviewers must not review their own work and should recuse themselves from proposals where a financial, professional, personal, or other material conflict could reasonably undermine impartiality. Maintainers review source quality, safety boundaries, duplication, generated-artifact effects, test evidence, and implementation scope before approving a repository change. Deterministic reputation recognizes accepted work but never conveys authority, verification status, or role eligibility.

## Moderation and reports

Reports, especially security concerns, are private application records. They must not be copied into public issues, review comments, or profile pages. Administrators and maintainers handle reports discreetly, record a bounded resolution, and retain only the minimum necessary information. Account suspension limits community application access but does not rewrite repository history. Unpublished private drafts are deleted on account deletion; published history is preserved without retaining the deleted account identity.

## Repository controls

The project recommends protected default branches that require pull-request review, passing validation, restricted direct pushes, and an up-to-date branch before merge. These are recommended operational controls, not a claim about current hosting configuration. The repository deliberately does not create a `CODEOWNERS` file with invented maintainers. See [the contribution workflow](docs/contribution-workflow.md), [moderation policy](docs/moderation.md), and [security policy](SECURITY.md) for operational details.
