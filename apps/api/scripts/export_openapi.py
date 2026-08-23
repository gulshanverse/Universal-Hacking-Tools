"""Export FastAPI’s generated OpenAPI contract; never manually edit its output."""
from pathlib import Path
import json
import sys

API_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = API_ROOT.parents[1]
for candidate in (API_ROOT, REPOSITORY_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))
from app.main import app


target = Path(__file__).resolve().parents[1] / "openapi.json"
target.write_text(json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(f"Wrote {target}")
