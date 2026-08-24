# Production Rate-Limit Policy

The repository currently uses bounded **in-process** limiters keyed by client address and route. They are validated for a single process and reduce accidental or basic abuse; they are not a distributed enforcement mechanism. A multi-instance public deployment requires an independently selected edge, gateway, or shared limiter before this policy can be considered verified.

| Route family | Current in-process policy | Purpose | Production deployment requirement |
| --- | --- | --- | --- |
| Registration, verification, login, reset | 8 requests per 10 minutes per client/path | Limit credential and enumeration abuse | Enforce equivalent or stricter trusted edge/shared policy; avoid user-name/email keys in logs. |
| Community profiles | 12 per hour per client/path | Limit profile update churn | Preserve CSRF and owner checks; monitor only aggregate failures. |
| Community proposals | 10 per hour per client/path | Limit proposal spam | Keep controlled-template validation, moderation, audit, and review requirements. |
| Private reports | 20 per hour per client/path | Limit report spam while permitting security reporting | Never make reporting public or log report content. |
| Reviews/moderation | 60 per hour per client/path | Bound privileged workflow actions | Role/RBAC and audit controls remain authoritative. |
| Graph, search-like expensive reads, paths, labs | 60 per minute per client/path plus route parameter caps | Protect bounded deterministic work | Preserve graph depth/nodes/edges/path caps and lab lifecycle/resource boundaries. |
| Recommendations | 30 per minute per client/path | Bound private deterministic computation | Preserve owner scope and private no-store responses. |

Request body, URL, headers, pagination, graph depth/nodes/edges/path, query contracts, and controlled proposal fields remain independent limits; rate limiting does not replace input validation. CAPTCHA is not configured because no verified abuse evidence warrants it. The edge/WAF, bot policy, multi-instance rate storage, and alert thresholds are **blocked — external prerequisites unavailable**.
