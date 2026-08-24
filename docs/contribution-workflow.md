# Contribution Workflow

Every contribution uses a constrained type and finite state machine. Proposal content is versioned so a reviewer can compare the canonical generated context, the submitted revision, and later revisions without overwriting history.

```text
draft → submitted → validation-failed | queued → under-review
under-review → changes-requested | approved | rejected
draft/submitted/queued/changes-requested → withdrawn
approved → merged → published
```

Only the server performs transitions. Contributors may edit only drafts and changes-requested records, and may withdraw only editable states. Reviewers may request changes, reject, or recommend approval; a reviewer cannot approve their own proposal. Maintainers perform final approval and publication state updates. No transition changes canonical knowledge automatically.

## Git handoff

When a maintainer chooses a handoff, the server prepares a controlled proposed file plan from the contribution type and allowlisted fields. It passes this data to a Git provider adapter. The adapter can report `queued`, `failed`, or `created`; it never reports a pull request URL unless the provider confirmed it. The adapter must use a dedicated branch, run repository validation in the resulting pull request, avoid auto-merge, and never bypass repository protections.

If no provider credential is configured, the application retains the approved proposal and presents a manual Git workflow. The browser never receives a GitHub token and cannot select repository paths, run Git, or submit generated artifacts.
