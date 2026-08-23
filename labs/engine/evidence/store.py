"""Ephemeral JSON evidence storage with conservative secret screening."""
from pathlib import Path
from datetime import datetime, timezone
import json, re

SECRET_PATTERN = re.compile(r"BEGIN (?:RSA|OPENSSH|EC|DSA) PRIVATE KEY|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|(?:password|passphrase|api[_ -]?key|access[_ -]?token|secret)\s*[:=]", re.IGNORECASE)


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe(value):
    text = json.dumps(value, sort_keys=True)
    if SECRET_PATTERN.search(text):
        raise ValueError("evidence contains a blocked secret-like pattern")
    return value


def evidence_path(instance_dir):
    return Path(instance_dir) / "evidence.json"


def load(instance_dir):
    path = evidence_path(instance_dir)
    if not path.exists(): return []
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, list) else []


def record(instance_dir, instance_id, task_id, evidence_id, evidence_type, value):
    value = _safe(value)
    records = load(instance_dir)
    item = {"instance_id": instance_id, "task_id": task_id, "evidence_id": evidence_id, "type": evidence_type, "recorded_at": now(), "value": value}
    records.append(item)
    evidence_path(instance_dir).write_text(json.dumps(records, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return item


def clear(instance_dir):
    path = evidence_path(instance_dir)
    if path.exists(): path.unlink()


def validate(instance_dir, definition):
    records = load(instance_dir)
    known = {item["id"]: item for item in definition.get("evidence", [])}
    errors = []
    for item in records:
        if item.get("evidence_id") not in known: errors.append(f"unknown evidence id: {item.get('evidence_id')}")
        if item.get("instance_id") != definition.get("_instance_id", item.get("instance_id")): errors.append("evidence instance mismatch")
        try: _safe(item.get("value"))
        except ValueError as exc: errors.append(str(exc))
    return sorted(set(errors)), records
