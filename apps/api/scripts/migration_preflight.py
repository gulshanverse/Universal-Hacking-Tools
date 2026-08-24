"""Read-only migration preflight; never applies a migration or prints a database URL."""
from __future__ import annotations

import json
from app.state.migration import migration_status


def main() -> int:
    result = {"operation": "migration-preflight", **migration_status()}
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
