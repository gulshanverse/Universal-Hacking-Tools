# Phase 7–8 Web Platform

The web platform is a responsive knowledge archive powered by the versioned API. It adds no alternate content model: the browser receives API responses, and the API receives deterministic generated contracts. Search is global and keyboard reachable, relationship views have accessible list alternatives, and every page preserves the repository’s safety and uncertainty language. Private dashboard views reference generated entities rather than copying knowledge content into browser state.

## Experience model

The selected **Signal Archive** direction uses a dark atlas navigation plane, warm long-form reading surfaces, teal relationship cues, and copper provenance accents. Verification status always includes text. The relationship explorer deliberately limits depth and result count instead of attempting to render the complete graph at once.

## Accessibility

The client provides semantic headings, landmark navigation, a first-focus skip link, visible focus styling, labeled search, keyboard global search focus (`Ctrl/⌘+K`), focusable filters, descriptive status labels, and a tabular alternative for relationship cards. It responds to small viewports and honors `prefers-reduced-motion` for nonessential transitions.

## SEO and public metadata

Route-specific titles, canonical URLs, Open Graph metadata, `robots.txt`, and `sitemap.xml` are included where useful. SEO text remains grounded in generated metadata; it does not add fabricated claims, testimonials, rankings, or performance figures.

## Browser data boundary

The browser does not access repository files, GitHub tokens, CI configuration, or local fixture paths. Public pages use the versioned public contract. Private account pages use credentialed requests with opaque HttpOnly session cookies; the JavaScript client does not store account tokens, passwords, verification/reset tokens, or notes in local storage. A readable CSRF cookie is echoed only in the `X-CSRF-Token` header for unsafe authenticated requests. The existing random local-lab session ID remains ephemeral in `sessionStorage` for fixture ownership, while any signed-in retained lab record contains only a minimal completion summary. Notes are displayed as plain text and no public profile, community, telemetry, or analytics feature is introduced.
