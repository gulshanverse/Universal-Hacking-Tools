"""Generate a deterministic route-security matrix from registered API routes."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.main import app


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "generated" / "api-route-security-matrix.json"
PRIVATE_PREFIXES = ("/api/v1/me", "/api/v1/auth", "/api/v1/community/review", "/api/v1/community/maintain", "/api/v1/community/admin")


def dependency_names(dependant) -> set[str]:
    names = {getattr(dependant.call, "__name__", "")}
    for child in dependant.dependencies:
        names.update(dependency_names(child))
    return names


def route_record(route, path: str) -> dict:
    names = dependency_names(route.dependant)
    methods = sorted(method for method in route.methods if method not in {"HEAD", "OPTIONS"})
    mutation = any(method in {"POST", "PUT", "PATCH", "DELETE"} for method in methods)
    authenticated = "csrf_protected" in names or "current_principal" in names or "optional_principal" in names
    role = "public"
    if path.startswith("/api/v1/community/admin"):
        role = "administrator"
    elif path.startswith("/api/v1/community/maintain"):
        role = "maintainer"
    elif path.startswith("/api/v1/community/review"):
        role = "reviewer"
    elif path.startswith("/api/v1/me") or path.startswith("/api/v1/auth"):
        role = "authenticated owner/session"
    csrf = mutation and "csrf_protected" in names
    rate_limit = "security-sensitive local limiter" if "rate_guard" in names else "bounded local limiter" if "expensive" in names else "route-specific or deployment edge policy required"
    sensitivity = "private application state" if path.startswith(PRIVATE_PREFIXES) else "public generated knowledge" if path.startswith("/api/v1/") else "operational metadata"
    if path in {"/api/v1/health", "/api/v1/live", "/api/v1/ready", "/api/v1/health/database"}:
        sensitivity = "minimal operational metadata"
    return {"path": path, "methods": methods, "access": "authenticated" if authenticated else "public", "minimum_role": role, "mutation": mutation, "csrf_required": csrf, "rate_limit": rate_limit, "input_validation": "FastAPI/Pydantic route contracts and bounded query constraints", "response_sensitivity": sensitivity}


def matrix() -> dict:
    records = []
    for included in app.routes:
        router = getattr(included, "original_router", None)
        if router is None:
            continue
        for route in getattr(router, "routes", []):
            if hasattr(route, "dependant"):
                records.append(route_record(route, f"/api/v1{route.path}"))
    records.sort(key=lambda item: (item["path"], item["methods"]))
    return {"schema_version": "1.0", "scope": "registered API route security classification; deployment-edge limits remain an external prerequisite", "routes": records}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(matrix(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content:
            raise SystemExit("API route security matrix is stale; run apps/api/scripts/generate_route_security_matrix.py")
        return 0
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
