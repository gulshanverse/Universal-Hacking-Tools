# Phase 8 Application-State Database

PostgreSQL stores **application state only**. The repository’s Markdown/YAML content and generated JSON contracts remain authoritative for cybersecurity knowledge. No table mirrors tools, vulnerabilities, concepts, techniques, technologies, controls, lab definitions, or learning-path definitions.

## Schema boundaries

| Table group | Purpose | Knowledge boundary |
| --- | --- | --- |
| `users`, `sessions`, verification/reset tokens | Minimal account and session lifecycle | No public content copied into rows |
| `user_profiles`, `learning_goals`, `user_learning_goals` | Private learner preferences and controlled goal mapping | Goal targets reference repository learning-path IDs |
| `entity_progress`, `learning_path_progress` | Private historical progress keyed by repository entity IDs and knowledge version | Content remains resolved from generated contracts |
| `bookmarks`, `private_notes` | Private learner organization and plain-text annotations | Bookmarks/notes refer to existing entity IDs, not duplicated content |
| `lab_attempts`, `lab_task_progress` | Minimal educational outcome summaries | Raw local runtime evidence remains ephemeral |
| `achievements`, `user_achievements`, `recommendation_snapshots` | Deterministic rules and auditable private recommendation output | Rules consume generated graph/contracts, not DB knowledge copies |

The initial Alembic migration is version-controlled under `apps/api/alembic/versions/`. It creates foreign keys, per-user unique constraints, status checks, constrained note length, token/session expiry indexes, and query indexes for ownership lookups. Migration downgrade drops Phase 8 state tables in reverse dependency order; production changes must be tested and backed up before use.

## Local development and test strategy

`docker-compose.yml` provides a development-only PostgreSQL service with non-production credentials and an isolated named volume. `make db-up`, `make db-migrate`, `make db-seed`, and `make db-reset` are local workflows; the reset target is deliberately destructive and never has an HTTP equivalent. Tests use an isolated database URL. CI supplies disposable PostgreSQL service state; local fast tests may use a temporary SQLite database only where SQLAlchemy behavior is compatible, while migration and integration gates are designed for PostgreSQL.

## Retention and deletion

Sessions and verification/reset tokens expire automatically. Notes, bookmarks, goals, progress, achievements, recommendation snapshots, and lab-attempt summaries are retained only while the account exists and are deleted on account deletion. Public knowledge and public lab definitions are unaffected. Raw Phase 6 local evidence is not copied into the database.

## Backup and rollback design

Production backup implementation is deferred. Before production, backups must be encrypted, retained according to a documented schedule, access-controlled, and restore-tested. A migration rollout requires a tested backup, forward migration validation, readiness checks, and an explicit downgrade or data-restoration plan; no migration is assumed reversible merely because it has a downgrade function.
