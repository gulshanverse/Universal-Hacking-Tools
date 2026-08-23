"""Fail when the committed OpenAPI contract differs from FastAPI’s generated schema."""
from pathlib import Path
import json
import sys

API_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = API_ROOT.parents[1]
sys.path[:0] = [str(API_ROOT), str(REPOSITORY_ROOT)]
from app.main import app

target = API_ROOT / "openapi.json"
expected = json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n"
if not target.exists() or target.read_text(encoding="utf-8") != expected:
    raise SystemExit("OpenAPI contract is stale; run python3 apps/api/scripts/export_openapi.py")
print("OpenAPI contract is current.")
