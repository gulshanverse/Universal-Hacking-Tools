"""Safe reference runner: reads committed synthetic fixtures only."""
from pathlib import Path
import json

from labs.engine.definition import fixture_path
from labs.engine.validation.safety_validator import ALLOWED_ACTIONS


def run_action(definition, action, target):
    if action not in ALLOWED_ACTIONS or action not in definition.get("allowed_actions", []):
        raise ValueError(f"action is not allowlisted: {action}")
    path = fixture_path(definition, target)
    if path is None or not path.is_file():
        raise ValueError(f"target fixture is unavailable: {target}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"fixture is invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError("fixture must contain an object")
    return {"action": action, "target": target, "fixture": path.relative_to(Path(__file__).resolve().parents[1]).as_posix(), "observation": value}
