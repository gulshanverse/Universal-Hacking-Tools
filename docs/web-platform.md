# Phase 7–9 Web Platform

The web platform is a responsive knowledge archive powered by the versioned API. It adds no alternate content model: the browser receives API responses, and the API receives deterministic generated contracts. Search is global and keyboard reachable, relationship views have accessible list alternatives, and every page preserves the repository’s safety and uncertainty language. Private dashboard views reference generated entities rather than copying knowledge content into browser state.

## Experience model

The selected **Signal Archive** direction uses a dark atlas navigation plane, warm long-form reading surfaces, teal relationship cues, and copper provenance accents. Verification status always includes text. Phase 9 adds `/explore` and `/explore/{entity}` as shareable public graph views with explicit depth, type, relationship, and trust filters; direct graph search focus; deterministic path mode; visual zoom/pan/select/reset controls; and a selected-node panel. It deliberately limits depth and result count instead of attempting to render the complete graph at once.

## Accessibility

The client provides semantic headings, landmark navigation, a first-focus skip link, visible focus styling, labeled search, keyboard global search focus (`Ctrl/⌘+K`), focusable filters, descriptive status labels, and a tabular alternative for relationship cards. Phase 9 keeps the SVG map `aria-hidden` and makes every core action available through the **Accessible Relationship Explorer** table: select a node, inspect type/trust/distance, follow entity links, change filters, or request a path without operating the map. A polite live region announces selection, bounded loading, path results, and truncation. It responds to small viewports and honors `prefers-reduced-motion` for nonessential transitions.

## SEO and public metadata

Route-specific titles, canonical URLs, Open Graph metadata, `robots.txt`, and `sitemap.xml` are included where useful. `/dashboard/*` and `/explore/orphans` are excluded from indexing; public entity-centered explorer URLs do not contain private progress. SEO text remains grounded in generated metadata; it does not add fabricated claims, testimonials, rankings, or performance figures.

## Browser data boundary

The browser does not access repository files, GitHub tokens, CI configuration, or local fixture paths. Public pages use the versioned public contract. Graph UI state is URL/local component state only; it is not stored in PostgreSQL. Public graph export contains generated nodes and relationships only. Private account pages use credentialed requests with opaque HttpOnly session cookies; the JavaScript client does not store account tokens, passwords, verification/reset tokens, or notes in local storage. A readable CSRF cookie is echoed only in the `X-CSRF-Token` header for unsafe authenticated requests. The existing random local-lab session ID remains ephemeral in `sessionStorage` for fixture ownership, while any signed-in retained lab record contains only a minimal completion summary. Notes are displayed as plain text and no public profile, community, telemetry, or analytics feature is introduced.
