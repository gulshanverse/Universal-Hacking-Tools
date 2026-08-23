"""Load deterministic JSON-in-YAML lab definitions without third-party dependencies."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
LAB_ROOT = ROOT / "labs"
DEFINITION_ROOT = LAB_ROOT / "definitions"
FIXTURE_ROOT = LAB_ROOT / "fixtures"


def definition_paths():
    return sorted(DEFINITION_ROOT.glob("*.yaml"))


def load_definition(path_or_id):
    path = Path(path_or_id)
    if path.suffix != ".yaml":
        path = DEFINITION_ROOT / (str(path_or_id) + ".yaml")
    if not path.is_absolute():
        path = ROOT / path
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: definition is not valid JSON-compatible YAML ({exc})") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path}: definition must be an object")
    value["_path"] = path.relative_to(ROOT).as_posix()
    return value


def fixture_path(definition, target):
    for item in definition.get("targets", []):
        if item.get("id") == target:
            relative = Path(str(item.get("fixture", "")))
            if relative.is_absolute() or ".." in relative.parts:
                return None
            candidate = (FIXTURE_ROOT / relative).resolve()
            try:
                candidate.relative_to(FIXTURE_ROOT.resolve())
            except ValueError:
                return None
            return candidate
    return None
