"""Filesystem-backed, disposable lifecycle for safe local-fixture labs."""
from pathlib import Path
from datetime import datetime, timezone
import json, shutil, uuid

from labs.engine.definition import load_definition, DEFINITION_ROOT
from labs.engine.catalog import graph_ids
from labs.engine.validation.safety_validator import validate_definition
from labs.engine.evidence import store
from labs.engine.assessment.engine import assess
from labs.runners.local_fixture import run_action

DEFAULT_STATE_ROOT = Path("/tmp/uht-labs")
TRANSITIONS = {
    "start": {"ready", "stopped"},
    "stop": {"ready", "running", "paused"},
    "reset": {"ready", "running", "paused", "stopped", "failed"},
    "destroy": {"defined", "creating", "ready", "running", "paused", "stopping", "stopped", "resetting", "failed"},
}


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class LabManager:
    def __init__(self, state_root=None):
        self.state_root = Path(state_root or DEFAULT_STATE_ROOT).expanduser().resolve()
        self.instances_root = self.state_root / "instances"
        self.instances_root.mkdir(parents=True, exist_ok=True)

    def definition(self, lab_id):
        return load_definition(lab_id)

    def validate(self, lab_id):
        definition = self.definition(lab_id)
        return definition, validate_definition(definition, fixture_root=Path(__file__).resolve().parents[2] / "fixtures", graph_ids=graph_ids())

    def list_instances(self):
        result = []
        for path in sorted(self.instances_root.iterdir() if self.instances_root.exists() else []):
            if path.is_dir() and (path / "state.json").exists():
                result.append(self._read_state(path))
        return result

    def _instance_dir(self, instance_id):
        path = (self.instances_root / instance_id).resolve()
        try: path.relative_to(self.instances_root.resolve())
        except ValueError: raise ValueError("invalid instance id")
        return path

    def _read_state(self, path):
        try: return json.loads((path / "state.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc: raise ValueError(f"invalid instance state: {path}") from exc

    def _get(self, instance_id):
        path = self._instance_dir(instance_id)
        if not (path / "state.json").exists(): raise ValueError(f"unknown instance: {instance_id}")
        state = self._read_state(path)
        definition = self.definition(state["lab_id"])
        definition["_instance_id"] = instance_id
        return path, state, definition

    def _write_state(self, path, state):
        state["updated_at"] = now()
        (path / "state.json").write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def _audit(self, path, event, state, **details):
        item = {"event": event, "at": now(), "instance_id": state["instance_id"], "lab_id": state["lab_id"]}
        item.update({key: value for key, value in details.items() if key in {"task_id", "evidence_id", "assessment_status"}})
        with (path / "audit.jsonl").open("a", encoding="utf-8") as handle: handle.write(json.dumps(item, sort_keys=True) + "\n")

    def _active_for_lab(self, lab_id):
        return [item for item in self.list_instances() if item.get("lab_id") == lab_id and item.get("state") in {"defined", "creating", "ready", "running", "paused", "stopping", "resetting"}]

    def create(self, lab_id, dry_run=False):
        definition, (errors, warnings) = self.validate(lab_id)
        if errors: raise ValueError("unsafe or invalid lab definition: " + "; ".join(errors))
        if len(self._active_for_lab(lab_id)) >= definition["environment"]["resources"]["max_instances"]: raise ValueError("maximum active instances reached for lab")
        plan = {"lab_id": lab_id, "name": definition["name"], "environment": definition["environment"], "targets": definition["targets"], "allowed_actions": definition["allowed_actions"], "evidence": definition["evidence"], "safety": definition["safety"], "timeout_seconds": definition["environment"]["resources"]["execution_timeout"]}
        if dry_run: return {"dry_run": True, "plan": plan}
        instance_id = f"lab-{lab_id}-{uuid.uuid4().hex[:8]}"
        path = self._instance_dir(instance_id)
        path.mkdir(parents=True)
        state = {"instance_id": instance_id, "lab_id": lab_id, "state": "ready", "created_at": now(), "updated_at": now()}
        manifest = {"lab_id": lab_id, "instance_id": instance_id, "created_at": state["created_at"], "definition": definition["_path"], "safety": {"internet_access": False, "isolated": True, "authorized_only": True}, "resources": definition["environment"]["resources"], "targets": definition["targets"], "allowed_actions": definition["allowed_actions"], "retention": "ephemeral"}
        (path / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (path / "evidence.json").write_text("[]\n", encoding="utf-8")
        (path / "audit.jsonl").touch()
        self._write_state(path, state); self._audit(path, "lab-created", state)
        return self.status(instance_id)

    def _transition(self, instance_id, operation, next_state, event):
        path, state, definition = self._get(instance_id)
        if state["state"] not in TRANSITIONS[operation]: raise ValueError(f"invalid transition: {state['state']} -> {operation}")
        state["state"] = next_state; self._write_state(path, state); self._audit(path, event, state)
        return self.status(instance_id)

    def start(self, instance_id):
        return self._transition(instance_id, "start", "running", "lab-started")

    def stop(self, instance_id):
        return self._transition(instance_id, "stop", "stopped", "lab-stopped")

    def reset(self, instance_id):
        path, state, definition = self._get(instance_id)
        if state["state"] not in TRANSITIONS["reset"]: raise ValueError(f"invalid transition: {state['state']} -> reset")
        store.clear(path)
        state["state"] = "ready"; state["reset_at"] = now(); self._write_state(path, state); self._audit(path, "lab-reset", state)
        return self.status(instance_id)

    def destroy(self, instance_id):
        path, state, definition = self._get(instance_id)
        if state["state"] not in TRANSITIONS["destroy"]: raise ValueError(f"invalid transition: {state['state']} -> destroy")
        store.clear(path)
        for name in ["manifest.json", "audit.jsonl", "evidence.json"]:
            candidate = path / name
            if candidate.exists(): candidate.unlink()
        state["state"] = "destroyed"; state["destroyed_at"] = now(); self._write_state(path, state)
        return self.status(instance_id)

    def status(self, instance_id):
        path, state, definition = self._get(instance_id)
        result = dict(state)
        result["safety"] = {"authorized_only": definition["safety"]["authorized_only"], "internet_access": definition["safety"]["internet_access"], "isolation_required": definition["safety"]["isolation_required"]}
        result["evidence_count"] = len(store.load(path)) if (path / "evidence.json").exists() else 0
        return result

    def run_task(self, instance_id, task_id):
        path, state, definition = self._get(instance_id)
        if state["state"] != "running": raise ValueError("tasks can run only in running state")
        task = next((item for item in definition.get("tasks", []) if item.get("id") == task_id), None)
        if task is None: raise ValueError(f"unknown task: {task_id}")
        result = run_action(definition, task["action"], task["target"])
        recorded = store.record(path, instance_id, task_id, task["evidence_id"], next(item["type"] for item in definition["evidence"] if item["id"] == task["evidence_id"]), result["observation"])
        self._audit(path, "evidence-recorded", state, task_id=task_id, evidence_id=task["evidence_id"])
        return {"task": task, "evidence": recorded}

    def evidence(self, instance_id):
        path, state, definition = self._get(instance_id)
        return {"instance_id": instance_id, "records": store.load(path), "validation": store.validate(path, definition)[0]}

    def submit_evidence(self, instance_id, task_id, evidence_id, value):
        """Record structured, allowlisted evidence without accepting files or commands."""
        path, state, definition = self._get(instance_id)
        if state["state"] != "running": raise ValueError("evidence can be submitted only in running state")
        task = next((item for item in definition.get("tasks", []) if item.get("id") == task_id), None)
        if task is None: raise ValueError(f"unknown task: {task_id}")
        if task.get("evidence_id") != evidence_id: raise ValueError("evidence id is not allowed for this task")
        evidence = next((item for item in definition.get("evidence", []) if item.get("id") == evidence_id), None)
        if evidence is None: raise ValueError(f"unknown evidence id: {evidence_id}")
        recorded = store.record(path, instance_id, task_id, evidence_id, evidence["type"], value)
        self._audit(path, "evidence-submitted", state, task_id=task_id, evidence_id=evidence_id)
        return recorded

    def assess(self, instance_id):
        path, state, definition = self._get(instance_id)
        errors, records = store.validate(path, definition)
        if errors: raise ValueError("invalid evidence: " + "; ".join(errors))
        result = assess(definition, records)
        self._audit(path, "assessment-completed", state, assessment_status=result["status"])
        return result
