# Phase 7–8 Knowledge Web Client

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

`NEXT_PUBLIC_API_URL` must point to the versioned API, typically `http://127.0.0.1:8000/api/v1`. Include the actual web origin in `UHT_ALLOWED_ORIGINS` when exercising local lab controls.

## Routes

| Route | Purpose |
| --- | --- |
| `/`, `/explore`, `/search` | API-backed overview, discovery, and deterministic search |
| `/tools`, `/vulnerabilities`, `/concepts`, `/techniques`, `/technologies`, `/defensive-controls` | Paginated generated collections |
| `/tool/{id}`, `/vulnerability/{id}`, and similar | Entity detail with trust, sources, prerequisites, and bounded relationships |
| `/labs`, `/labs/{id}` | Lab metadata and, for approved definitions only, constrained local-fixture controls |
| `/learning-paths`, `/learning-paths/{id}` | Learning progression and relationships |
| `/about/health`, `/contribute` | Generated health limits and read-only contribution guidance |
| `/login`, `/register`, `/verify-email`, `/forgot-password`, `/reset-password` | Private account lifecycle forms using the configured delivery channel |
| `/dashboard`, `/dashboard/*` | Protected owner-only goals, recommendations, skills, learning paths, safe-lab summaries, bookmarks, notes, and settings |

## Safety and privacy

The local lab workspace has no terminal, target field, arbitrary command, file upload, remote execution, public profile, or community feature. It shows only predefined safe tasks, hints, structured evidence, deterministic assessment, reset, and destroy controls for a previously validated local fixture. The browser creates a random ID in `sessionStorage` solely to scope an ephemeral local lab instance; it is not an identity and is not transmitted to any third party. When a user is signed in, the browser can request retention of only a minimal assessment summary; raw evidence is never persisted.

Private account state uses opaque HttpOnly cookies rather than browser-stored bearer tokens. The client reads only a non-sensitive CSRF cookie to set `X-CSRF-Token` on unsafe authenticated requests. Passwords, session values, verification/reset tokens, and note bodies are not placed in local storage. Notes render as plain text. Public knowledge pages stay usable when the private database is unavailable; protected state pages show a clear unavailable state.

## Validation

```bash
pnpm test
pnpm typecheck
NODE_ENV=production pnpm build
UHT_WEB_URL=http://127.0.0.1:3001 pnpm test:e2e
```

The browser test uses a local Chromium binary and requires a separately running API plus web server. It covers navigation, search, entity exploration, keyboard skip-link focus, mobile overflow, constrained safe lab lifecycle, and Phase 8 account/private-state flows when configured with disposable synthetic data.
