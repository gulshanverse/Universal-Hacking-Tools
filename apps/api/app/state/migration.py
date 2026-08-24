"""Read-only Alembic revision inspection shared by operational preflight scripts."""
from __future__ import annotations

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import text

from .database import database_ready, engine


def migration_status() -> dict[str, str | None]:
    root = Path(__file__).resolve().parents[4]
    config = Config(str(root / "apps" / "api" / "alembic.ini"))
    config.set_main_option("script_location", str(root / "apps" / "api" / "alembic"))
    expected = ScriptDirectory.from_config(config).get_current_head()
    result: dict[str, str | None] = {"database": "unavailable", "expected_revision": expected, "actual_revision": None, "status": "blocked"}
    if database_ready():
        with engine().connect() as connection:
            result["actual_revision"] = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one_or_none()
        result["database"] = "reachable"
        result["status"] = "validated" if result["actual_revision"] == expected else "blocked"
    return result
