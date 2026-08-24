"""Verify an operator-restored isolated database without performing restore or migration work."""
from __future__ import annotations

import json
import os

from app.services.artifacts import artifacts
from app.state.config import settings
from app.state.database import database_ready
from app.state.migration import migration_status


def main() -> int:
    config = settings()
    if config.environment not in {"test", "staging"} or os.getenv("UHT_RESTORE_DRILL_TARGET") != "isolated":
        print(json.dumps({"status": "blocked", "evidence": "restore verification requires UHT_ENVIRONMENT=test or staging and UHT_RESTORE_DRILL_TARGET=isolated"}, sort_keys=True))
        return 2
    artifacts_ready, _missing = artifacts.ready()
    database_ok = database_ready()
    migration = migration_status()
    status = "validated" if artifacts_ready and database_ok and migration["status"] == "validated" else "blocked"
    print(json.dumps({"status": status, "artifacts": "validated" if artifacts_ready else "blocked", "database": "validated" if database_ok else "blocked", "migration": migration["status"], "scope": "isolated restore verification only"}, sort_keys=True))
    return 0 if status == "validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
