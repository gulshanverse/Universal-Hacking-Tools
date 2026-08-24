"""Production configuration preflight that never prints secret values or mutates state."""
from __future__ import annotations

import json

from app.services.artifacts import artifacts
from app.state.config import settings, validate_production_secrets
from app.state.database import database_ready


def main() -> int:
    checks: list[dict[str, str]] = []
    try:
        config = settings()
        if not config.is_production:
            checks.append({"name": "environment", "status": "blocked", "evidence": "UHT_ENVIRONMENT is not production"})
            checks.append({"name": "secret-and-origin-policy", "status": "not-configured", "evidence": "production secret and origin validation is not applicable until production mode is selected"})
        else:
            checks.append({"name": "environment", "status": "validated", "evidence": "production mode selected"})
            validate_production_secrets()
            checks.append({"name": "secret-and-origin-policy", "status": "validated", "evidence": "required production values passed validation"})
    except RuntimeError as exc:
        checks.append({"name": "secret-and-origin-policy", "status": "blocked", "evidence": str(exc)})
    try:
        ready, missing = artifacts.ready()
        checks.append({"name": "generated-artifacts", "status": "validated" if ready else "blocked", "evidence": "required generated contracts available" if ready else "missing required generated contracts"})
    except Exception:
        checks.append({"name": "generated-artifacts", "status": "blocked", "evidence": "generated artifact inspection failed"})
    checks.append({"name": "private-database", "status": "validated" if database_ready() else "blocked", "evidence": "private database connection succeeded" if database_ready() else "private database connection unavailable"})
    overall = "READY" if checks and all(item["status"] == "validated" for item in checks) else "BLOCKED"
    print(json.dumps({"status": overall, "checks": checks}, sort_keys=True))
    return 0 if overall == "READY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
