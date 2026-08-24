# Community Security and Incident Response

Community input is untrusted. Profiles, proposal titles/descriptions, draft payloads, source links, report bodies, and review comments are stored and rendered as bounded plain text. The application does not render arbitrary HTML, execute Markdown, accept uploads, run binaries, invoke shells, fetch submitted URLs, or follow user-selected repository paths.

URL-bearing fields allow only normalized `https` URLs with a host. `javascript:`, `data:`, `vbscript:`, local file URLs, embedded credentials, and malformed URLs are rejected before persistence. Source authority classification is a review signal, not an automatic verification result.

## Incident process

> Detect → contain → investigate → fix → disclose appropriately → document.

Security reports are isolated from ordinary community listings, reviewer comments, and public profiles. Reporters can see their own submission status, while authorized administrators/maintainers use the repository’s [security policy](../SECURITY.md) and private disclosure channel to coordinate response. A public issue is created only after a maintainer determines that disclosure is appropriate.

Account suspension blocks profile changes, proposal creation/editing, reports, reviews, and comments while preserving existing public contribution history. Every moderation action writes an append-only audit event with actor, target, action, reason, and time.
