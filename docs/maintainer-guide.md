# Maintainer Guide

Maintainers make the final human governance decision after reviewing the contribution history, validation findings, reviewer comments, sources, safety implications, duplicate candidates, and graph/trust impact. Approved proposals remain proposed content until a controlled Git handoff has produced a pull request and the repository’s required CI and review protections have completed.

Use a dedicated branch and conventional pull request workflow for every accepted knowledge change. Do not bypass required review, force-push protected branches, auto-merge submissions, or expose provider credentials. If a handoff fails, retain the approved proposal with an honest failed state and resolve it manually; never claim that a pull request exists without a confirmed provider URL.

For security, copyright, or legal disputes, preserve the audit record, restrict access as appropriate, follow [SECURITY.md](../SECURITY.md), and resolve published content through a normal Git change and CI rather than an application deletion endpoint.
