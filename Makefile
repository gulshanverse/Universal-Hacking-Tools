.PHONY: api web api-test web-test web-build openapi dev

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

dev:
	@echo "Run 'make api' and 'make web' in separate terminals for local development."
