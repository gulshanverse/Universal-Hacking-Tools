# Phase 7–11 Knowledge Web Client

This Next.js web client is a responsive public and private view of the versioned API. It does not embed copies of knowledge entities or parse repository Markdown in the browser. The **Signal Archive** design makes relationships, verification state, provenance, local lab safety, and owner-only learning state visible without representing the project as an unrestricted security console.

## Local development

Run the API and web processes separately:

```bash
# terminal one, after following the root development workflow
make db-up && make db-migrate && make api

# terminal two
cd apps/web
cp .env.example .env.local
pnpm install
pnpm dev
```

`NEXT_PUBLIC_API_URL` must point to the versioned API, typically `http://127.0.0.1:8000/api/v1`. Include the actual web origin in `UHT_ALLOWED_ORIGINS` when exercising local lab or authenticated community controls; the production-like local browser suite uses `http://127.0.0.1:3001`.

## Routes

| Route | Purpose |
| --- | --- |
| `/`, `/explore`, `/explore/{entity}`, `/search` | API-backed overview, bounded graph exploration, shareable entity focus, and deterministic direct-first or graph-context search |
| `/tools`, `/vulnerabilities`, `/concepts`, `/techniques`, `/technologies`, `/defensive-controls` | Paginated generated collections |
| `/tool/{id}`, `/vulnerability/{id}`, and similar | Entity detail with trust, sources, prerequisites, and bounded relationships |
| `/labs`, `/labs/{id}` | Lab metadata and, for approved definitions only, constrained local-fixture controls |
| `/learning-paths`, `/learning-paths/{id}` | Learning progression and relationships |
| `/about/health`, `/contribute` | Generated health limits and read-only contribution guidance |
| `/login`, `/register`, `/verify-email`, `/forgot-password`, `/reset-password` | Private account lifecycle forms using the configured delivery channel |
| `/dashboard`, `/dashboard/*`, `/dashboard/knowledge-map` | Protected owner-only goals, recommendations, skills, learning paths, safe-lab summaries, bookmarks, notes, settings, and a private progress overlay over the same generated graph |
| `/explore/orphans` | Read-only graph-gap reviewer context; excluded from indexing and incapable of editing or approving relationships |
| `/community`, `/community/{username}`, `/community/contributions/{id}`, `/contribute` | Public opted-in community discovery and clear proposal workflow boundary; published application history is not a direct knowledge editor |
| `/dashboard/contributions`, `/dashboard/reputation`, `/dashboard/reports` | Protected contributor profile, controlled proposal, deterministic reputation, and private-report workspaces |
| `/review`, `/admin/community` | Restricted noindex reviewer/maintainer and administrator workspaces; client navigation is role-aware but the API is authoritative |

## Safety and privacy

The Phase 9 graph explorer remains a knowledge-navigation interface, not a security console. Its SVG map is supplementary: depth, type, relationship, and trust filters; graph focus; bounded path selection; node selection; zoom/pan/reset; and entity links remain available through conventional controls and a structured relationship table. Public graph export contains only generated nodes and relationship records. Phase 10 adds opt-in public profiles and proposal history plus controlled private collaboration forms, but still has no terminal, target field, arbitrary command, file upload, remote execution, public security reports, direct Git action, or browser-side knowledge mutation. The local lab workspace shows only predefined safe tasks, hints, structured evidence, deterministic assessment, reset, and destroy controls for a previously validated local fixture. The browser creates a random ID in `sessionStorage` solely to scope an ephemeral local lab instance; it is not an identity and is not transmitted to any third party. When a user is signed in, the browser can request retention of only a minimal assessment summary; raw evidence is never persisted.

Private account state uses opaque HttpOnly cookies rather than browser-stored bearer tokens. The client reads only a non-sensitive CSRF cookie to set `X-CSRF-Token` on unsafe authenticated requests. Passwords, session values, verification/reset tokens, and note bodies are not placed in local storage. Notes render as plain text. Public knowledge pages stay usable when the private database is unavailable; protected state pages show a clear unavailable state.

## Production boundary

When `UHT_ENVIRONMENT=production`, the browser build requires an explicit credential-free HTTPS `NEXT_PUBLIC_API_URL`; it must not fall back to localhost. `NEXT_PUBLIC_SITE_URL` and the API URL are public build values only—never place database, session, CSRF, Git-provider, or deployment credentials in a browser environment variable. Run `pnpm production-check` with explicit HTTPS example/target URLs to validate the public configuration shape without exposing values.

The production configuration emits a CSP compatible with the existing client, frame/no-sniff/referrer/permissions restrictions, and HSTS only in explicitly selected production mode. Dashboard, review, and administration routes receive private no-store/noindex headers. Production-safe not-found, access-limited, rate-limit, generic-error, and maintenance pages intentionally expose no diagnostics. A canonical host, TLS certificate, provider redirect behavior, CDN/WAF, and live header verification are **blocked — external prerequisites unavailable** until a hosting platform is selected and tested.

## Validation

```bash
pnpm test
pnpm typecheck
UHT_ENVIRONMENT=development NODE_ENV=production pnpm build
UHT_ENVIRONMENT=production NEXT_PUBLIC_API_URL=https://api.example.test/api/v1 NEXT_PUBLIC_SITE_URL=https://app.example.test pnpm production-check
UHT_WEB_URL=http://127.0.0.1:3001 pnpm test:e2e
```

The browser test uses a local Chromium binary and requires a separately running API plus web server. It covers navigation, direct search, bounded public graph focus/depth/path/table controls, keyboard skip-link focus, mobile overflow, constrained safe lab lifecycle, Phase 8–9 account/private-state and knowledge-map flows, and the Phase 10 contributor → reviewer → maintainer proposal lifecycle. The local Phase 10 journey asserts that an unconfigured server-side provider reports a failed handoff and a manual fallback rather than a false pull-request success.
