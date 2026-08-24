# Phase 7–11 Web Platform

The web platform is a responsive knowledge archive powered by the versioned API. It adds no alternate content model: the browser receives API responses, and the API receives deterministic generated contracts. Search is global and keyboard reachable, relationship views have accessible list alternatives, and every page preserves the repository’s safety and uncertainty language. Private dashboard views reference generated entities rather than copying knowledge content into browser state. Phase 10 adds a controlled proposal and review workspace, not a browser-side knowledge editor.

## Experience model

The selected **Signal Archive** direction uses a dark atlas navigation plane, warm long-form reading surfaces, teal relationship cues, and copper provenance accents. Verification status always includes text. Phase 9 adds `/explore` and `/explore/{entity}` as shareable public graph views with explicit depth, type, relationship, and trust filters; direct graph search focus; deterministic path mode; visual zoom/pan/select/reset controls; and a selected-node panel. It deliberately limits depth and result count instead of attempting to render the complete graph at once.

Phase 10 adds `/community`, opt-in public profile pages, public published-contribution history, a controlled contributor workspace, private reputation and report pages, and restricted `/review` and `/admin/community` workspaces. Proposal forms use semantic fields and fixed templates, show **PROPOSED CONTENT — NOT CANONICAL KNOWLEDGE**, submit through cookie/CSRF transport, and render all untrusted content as text. Review and moderation views are role-aware conveniences only; the API remains the authorization authority.

## Accessibility

The client provides semantic headings, landmark navigation, a first-focus skip link, visible focus styling, labeled search, keyboard global search focus (`Ctrl/⌘+K`), focusable filters, descriptive status labels, and a tabular alternative for relationship cards. Phase 9 keeps the SVG map `aria-hidden` and makes every core action available through the **Accessible Relationship Explorer** table: select a node, inspect type/trust/distance, follow entity links, change filters, or request a path without operating the map. A polite live region announces selection, bounded loading, path results, and truncation. It responds to small viewports and honors `prefers-reduced-motion` for nonessential transitions.

## SEO and public metadata

Route-specific titles, canonical URLs, Open Graph metadata, `robots.txt`, and `sitemap.xml` are included where useful. `/dashboard/*`, `/review`, `/admin/*`, and `/explore/orphans` are excluded from indexing; public entity-centered explorer URLs do not contain private progress. SEO text remains grounded in generated metadata; it does not add fabricated claims, testimonials, rankings, or performance figures.

## Browser data boundary

The browser does not access repository files, GitHub tokens, CI configuration, provider credentials, or local fixture paths. Public pages use the versioned public contract. Graph UI state is URL/local component state only; it is not stored in PostgreSQL. Public graph export contains generated nodes and relationships only. Private account pages use credentialed requests with opaque HttpOnly session cookies; the JavaScript client does not store account tokens, passwords, verification/reset tokens, report details, or notes in local storage. A readable CSRF cookie is echoed only in the `X-CSRF-Token` header for unsafe authenticated requests. The existing random local-lab session ID remains ephemeral in `sessionStorage` for fixture ownership, while any signed-in retained lab record contains only a minimal completion summary. Notes, proposals, reviews, and reports render as plain text. Public community pages expose only opted-in profile data and published contribution aggregates; private reports and moderation records remain private. The browser has no direct Git capability and must describe an unconfigured provider handoff as failed with a manual fallback.

## Phase 11 production boundary

Production browser builds require an explicit credential-free `NEXT_PUBLIC_API_URL`; when `UHT_ENVIRONMENT=production`, a missing value or non-HTTPS URL fails rather than silently falling back to a localhost API. `NEXT_PUBLIC_SITE_URL` and the API URL are public build-time configuration only and must never include database credentials, session secrets, CSRF secrets, or provider tokens.

The Next.js configuration emits a CSP compatible with the current application, frame protection, no-sniff, no-referrer, permissions restrictions, and HSTS only when the production environment is explicitly selected. Dashboard, review, and administration paths are marked `private, no-store` and `noindex, nofollow`. Production-safe 404, access-limited, rate-limited, generic-error, and maintenance pages display no stack trace, role information, account details, or diagnostics.

These are code-level controls. A canonical host, TLS certificate, CDN/WAF behavior, HTTP-to-HTTPS redirect, actual browser-header verification, and public deployment remain **blocked — external prerequisites unavailable** until a selected platform is configured and tested. See [production readiness](production-readiness.md).
