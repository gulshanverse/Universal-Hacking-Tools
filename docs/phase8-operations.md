# Phase 8 Operations

## Local development only

Copy `apps/api/.env.example` and `apps/web/.env.example` to local, untracked `.env` files. Start the development-only PostgreSQL container with `make db-up`, apply the versioned schema with `make db-migrate`, and optionally create the intentionally fake learner with `make db-seed`. The seed account is `developer@example.test`; its development-only password is printed by the seed command and must never be retained, deployed, or reused. Start `make api` and `make web` in separate terminals. Docker is not required for generated knowledge validation; the isolated SQLite workflow used by API tests is a compatibility check, not a production deployment topology.

`make db-reset` removes the local Compose volume before rebuilding and seeding it. It is deliberately destructive, is not exposed by HTTP, and must never target a shared or production database. The Compose credentials are local placeholders only.

## Migration, backup, and rollback

Use `alembic upgrade head` with `DATABASE_URL` set to the intended PostgreSQL database. Before any migration, take an encrypted, access-controlled database backup and rehearse `alembic downgrade -1` on a restored copy. Migration rollback changes schema only; it does not recreate deleted application-state rows. Keep knowledge changes in Git through the existing Markdown/YAML and generated-artifact workflow, not in PostgreSQL backups.

Run public knowledge in degraded read-only mode when PostgreSQL is unavailable: existing generated-contract routes remain available, while authenticated and state-changing routes return a clear service-unavailable response. The API never queues private writes while its database is unavailable.

Local PostgreSQL is development-only and configured through `.env`; production secrets belong in the deployment platform secret manager. Use explicit CORS origins, HTTPS, secure cookie mode outside development, redacted structured logs, and least-privilege database credentials. Do not log passwords, email unnecessarily, session identifiers, verification/reset tokens, note bodies, or sensitive lab evidence.

Before deployment, apply migrations to a tested backup, verify database readiness, validate OpenAPI freshness, run authorization and multi-user tests, build the web client, and test a disposable safe-lab lifecycle. Production backup automation, multi-instance rate limiting, email delivery operations, and public deployment are intentionally deferred.
