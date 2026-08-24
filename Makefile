.PHONY: api web api-test web-test web-build openapi dev db-up db-down db-migrate db-downgrade db-seed db-reset

api:
	PYTHONPATH=apps/api:. python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000

web:
	cd apps/web && pnpm dev

api-test:
	PYTHONPATH=apps/api:. python3 -m unittest discover -s apps/api/tests -v

web-test:
	cd apps/web && pnpm test

web-build:
	cd apps/web && pnpm build

openapi:
	python3 apps/api/scripts/export_openapi.py && PYTHONPATH=apps/api:. python3 apps/api/scripts/check_openapi.py

db-up:
	docker compose up -d db

db-down:
	docker compose down

db-migrate:
	cd apps/api && PYTHONPATH=. alembic upgrade head

db-downgrade:
	cd apps/api && PYTHONPATH=. alembic downgrade -1

db-seed:
	PYTHONPATH=apps/api:. python3 apps/api/scripts/seed_development.py

db-reset:
	@echo "WARNING: this deletes the local development PostgreSQL volume and all private application state."
	docker compose down -v
	docker compose up -d db
	$(MAKE) db-migrate
	$(MAKE) db-seed

dev:
	@echo "Run 'make db-up', then 'make db-migrate', then start 'make api' and 'make web' in separate terminals. Docker is optional outside local PostgreSQL development."
