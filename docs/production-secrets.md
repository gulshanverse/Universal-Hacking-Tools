# Production Secrets and Environment Variables

No production secret is stored in this repository. Production startup rejects missing, short, or recognizable placeholder session and CSRF secrets; it also requires an explicit PostgreSQL URL, HTTPS origins, trusted hosts, and secure cookies. This is a configuration gate, not evidence that a secret manager or production deployment exists.

## Environment-variable classification

| Variable family | Classification | Availability | Handling |
| --- | --- | --- | --- |
| `DATABASE_URL` | Secret, server-only, runtime | API process only | Use a least-privilege PostgreSQL account; do not place it in browser builds, logs, issues, or CI output. |
| `SESSION_SECRET`, `CSRF_SECRET` | Secret, server-only, runtime | API process only | Generate independent long random values. Production rejects placeholders and values shorter than 32 characters. |
| `UHT_ALLOWED_ORIGINS`, `UHT_TRUSTED_HOSTS` | Server-only, runtime | API process only | Explicit HTTPS public origins and host names; never wildcard credentialed origins. |
| `UHT_SECURE_COOKIES`, TTLs, request limits, log level | Server-only, runtime | API process only | Review per environment; production requires secure cookies. |
| `UHT_BUILD_VERSION`, `UHT_BUILD_COMMIT` | Server-only, build/runtime metadata | API health response | May identify a release, but must contain no token, URL credential, or infrastructure detail. |
| `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SITE_URL` | Public, build-time | Browser bundle | Must contain public HTTPS origins only; never include credentials, database values, or server secrets. |
| Git-provider credential | Optional secret, server-only, runtime | Not configured | Keep unavailable until a separately reviewed least-privilege integration exists; retain manual pull-request fallback. |

## Generation, storage, and access

Generate secrets with a cryptographically secure generator from the selected deployment platform or an approved local administrative environment. Store them in the deployment provider’s server-side secret facility or an organization-approved secret manager. Limit read access to the runtime identity and a small operational group. Never commit `.env` files containing real credentials, render secret values in deployment logs, or expose them through `/openapi.json`, health routes, browser configuration, errors, or support artifacts.

## Rotation and revocation

| Secret | Routine rotation | Emergency response | Expected effect |
| --- | --- | --- | --- |
| Session secret | Schedule after provider selection; record the change | Replace immediately after suspected disclosure | Existing opaque sessions become invalid because their HMAC hashes no longer match. |
| CSRF secret | Rotate with the session secret unless a documented staged process exists | Replace immediately after suspected disclosure | Existing CSRF tokens become invalid; active users must refresh or sign in again. |
| Database credential | Provider-defined schedule and least-privilege rollout | Revoke, create replacement, update runtime, test health, then retire old credential | Private-state access may be briefly unavailable during controlled rotation. |
| Git-provider credential | Only if integration is enabled | Revoke, disable provider use, audit handoffs and branches, then reissue least privilege | Handoffs fail safely and manual PR workflow remains available. |
| Deployment credential | Provider-defined schedule | Revoke, freeze deployment, audit access, and restore only after review | Deployment is blocked until a trusted credential is restored. |

No rotation, provider, or secret store is currently verified for a public deployment. These steps are a required runbook once external infrastructure is selected.
