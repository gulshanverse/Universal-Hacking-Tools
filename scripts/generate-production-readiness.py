"""Generate the deterministic repository production-readiness report without probing external infrastructure."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "generated" / "production-readiness.json"


def report() -> dict:
    items = [
        {"category": "application", "name": "repository application controls", "status": "configured", "evidence": "Phase 11 configuration, health, request-bound, and regression controls are versioned in the repository.", "timestamp": "not-recorded", "owner": "maintainers", "blocking": False},
        {"category": "database", "name": "production PostgreSQL", "status": "blocked", "evidence": "No production PostgreSQL provider, private connection, least-privilege roles, or TLS evidence is configured in this repository.", "timestamp": "not-recorded", "owner": "deployment operator", "blocking": True},
        {"category": "security", "name": "repository security controls", "status": "configured", "evidence": "Explicit production secret/origin validation, request boundaries, secure-cookie requirements, and CI gates are versioned; target-environment verification remains required.", "timestamp": "not-recorded", "owner": "maintainers", "blocking": False},
        {"category": "deployment", "name": "public deployment", "status": "blocked", "evidence": "No deployment provider, canonical host, or verified smoke target is configured.", "timestamp": "not-recorded", "owner": "deployment operator", "blocking": True},
        {"category": "observability", "name": "hosted logs and alerts", "status": "blocked", "evidence": "Privacy-safe structured application logs are configured in code; no external sink, dashboard, or alert route is configured.", "timestamp": "not-recorded", "owner": "deployment operator", "blocking": True},
        {"category": "backup", "name": "database backup", "status": "blocked", "evidence": "No production database provider, encrypted backup policy, retention setting, or restore evidence is configured.", "timestamp": "not-recorded", "owner": "deployment operator", "blocking": True},
        {"category": "recovery", "name": "production restore drill", "status": "blocked", "evidence": "An isolated restore procedure is documented, but no production backup source exists to test.", "timestamp": "not-recorded", "owner": "deployment operator", "blocking": True},
        {"category": "privacy", "name": "application data minimization", "status": "configured", "evidence": "Private-state and account-deletion boundaries are versioned; production retention and backup evidence depend on the selected provider.", "timestamp": "not-recorded", "owner": "maintainers", "blocking": False},
        {"category": "performance", "name": "production performance baseline", "status": "blocked", "evidence": "No staging or production target is configured for safe measurement.", "timestamp": "not-recorded", "owner": "deployment operator", "blocking": True},
        {"category": "documentation", "name": "production runbooks", "status": "configured", "evidence": "Versioned threat, architecture, deployment, recovery, incident, privacy, and readiness documentation is present.", "timestamp": "not-recorded", "owner": "maintainers", "blocking": False},
    ]
    return {"schema_version": "1.0", "scope": "repository readiness only; not a public deployment assertion", "overall_status": "BLOCKED", "decision": "BLOCKED", "items": items, "external_blockers": ["domain and DNS", "TLS certificate and redirect verification", "production PostgreSQL", "deployment provider", "production email delivery", "backup and restore evidence", "hosted monitoring and alerting"], "score_policy": "No readiness score is emitted because critical external blockers cannot be overridden by repository controls."}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(report(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content:
            raise SystemExit("production readiness report is stale; run scripts/generate-production-readiness.py")
        return 0
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
