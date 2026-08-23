"""Strict, offline validation for executable lab definitions."""
from pathlib import Path
import re

DIFFICULTIES = {"beginner", "intermediate", "advanced"}
PREREQUISITE_TYPES = {"required", "recommended", "helpful"}
EVIDENCE_TYPES = {"observation", "artifact", "finding", "configuration", "log-entry", "request-response", "screenshot-reference", "answer"}
ALLOWED_ACTIONS = {"inspect_fixture", "inspect_dns_record", "inspect_tls_metadata", "inspect_http_response", "inspect_log", "inspect_iac_manifest", "inspect_container_config", "record_answer"}
EXECUTION_MODES = {"documentation-only", "guided", "executable"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")


def _required(value, key, errors):
    if key not in value:
        errors.append(f"missing required field: {key}")


def _nonempty_string(value, key, errors):
    if not isinstance(value.get(key), str) or not value[key].strip():
        errors.append(f"{key} must be a non-empty string")


def validate_definition(definition, fixture_root=None, graph_ids=None):
    errors, warnings = [], []
    required = ["id", "name", "description", "difficulty", "category", "objectives", "prerequisites", "environment", "targets", "allowed_actions", "tasks", "evidence", "assessment", "cleanup", "safety", "learning"]
    for key in required:
        _required(definition, key, errors)
    if not isinstance(definition.get("id"), str) or not ID_RE.fullmatch(definition.get("id", "")):
        errors.append("id must match the lowercase slug format")
    for key in ["name", "description", "category"]:
        _nonempty_string(definition, key, errors)
    if definition.get("difficulty") not in DIFFICULTIES:
        errors.append("difficulty must be beginner, intermediate, or advanced")
    if not isinstance(definition.get("objectives"), list) or not definition["objectives"]:
        errors.append("objectives must be a non-empty list")
    errors.extend(_validate_safety(definition.get("safety"), definition.get("environment"), definition.get("cleanup")))
    allowed = definition.get("allowed_actions")
    if not isinstance(allowed, list) or not allowed or len(set(allowed)) != len(allowed):
        errors.append("allowed_actions must be a non-empty unique list")
    elif any(action not in ALLOWED_ACTIONS for action in allowed):
        errors.append("allowed_actions contains an unknown action")
    prereqs = definition.get("prerequisites")
    if not isinstance(prereqs, list):
        errors.append("prerequisites must be a list")
    else:
        seen = set()
        for item in prereqs:
            if not isinstance(item, dict) or not item.get("target") or item.get("type") not in PREREQUISITE_TYPES:
                errors.append("each prerequisite needs target and required/recommended/helpful type")
            else:
                marker = (item["target"], item["type"])
                if marker in seen: errors.append(f"duplicate prerequisite: {marker[0]}")
                seen.add(marker)
                if graph_ids is not None and not any(item["target"] == ident.split(":", 1)[-1] for ident in graph_ids):
                    errors.append(f"unknown prerequisite target: {item['target']}")
    targets = definition.get("targets")
    target_ids = set()
    if not isinstance(targets, list) or not targets:
        errors.append("targets must be a non-empty list")
    else:
        for target in targets:
            if not isinstance(target, dict): errors.append("target must be an object"); continue
            for key in ["id", "type", "fixture", "role"]: _required(target, key, errors)
            target_id = target.get("id", "")
            if target_id in target_ids: errors.append(f"duplicate target id: {target_id}")
            target_ids.add(target_id)
            if target.get("type") != "synthetic-fixture": errors.append(f"target {target_id}: only synthetic-fixture is allowed")
            fixture = Path(str(target.get("fixture", "")))
            if fixture.is_absolute() or ".." in fixture.parts or fixture.suffix != ".json": errors.append(f"target {target_id}: unsafe fixture path")
            if fixture_root is not None and not (Path(fixture_root) / fixture).is_file(): errors.append(f"target {target_id}: fixture does not exist")
    evidence = definition.get("evidence")
    evidence_ids = set()
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence must be a non-empty list")
    else:
        for item in evidence:
            if not isinstance(item, dict): errors.append("evidence entry must be an object"); continue
            for key in ["id", "type", "description", "required"]: _required(item, key, errors)
            if item.get("id") in evidence_ids: errors.append(f"duplicate evidence id: {item.get('id')}")
            evidence_ids.add(item.get("id"))
            if item.get("type") not in EVIDENCE_TYPES: errors.append(f"unknown evidence type: {item.get('type')}")
            if not isinstance(item.get("required"), bool): errors.append(f"evidence {item.get('id')}: required must be boolean")
    tasks = definition.get("tasks")
    task_ids = set()
    if not isinstance(tasks, list) or not tasks:
        errors.append("tasks must be a non-empty list")
    else:
        for item in tasks:
            if not isinstance(item, dict): errors.append("task entry must be an object"); continue
            for key in ["id", "objective", "description", "action", "target", "evidence_id"]: _required(item, key, errors)
            if item.get("id") in task_ids: errors.append(f"duplicate task id: {item.get('id')}")
            task_ids.add(item.get("id"))
            if item.get("action") not in set(allowed or []): errors.append(f"task {item.get('id')}: action is not allowlisted")
            if item.get("target") not in target_ids: errors.append(f"task {item.get('id')}: unknown target")
            if item.get("evidence_id") not in evidence_ids: errors.append(f"task {item.get('id')}: unknown evidence id")
            for hint in item.get("hints", []):
                if not isinstance(hint, dict) or hint.get("level") not in {1, 2, 3} or not str(hint.get("text", "")).strip(): errors.append(f"task {item.get('id')}: invalid hint")
    assessment = definition.get("assessment")
    if not isinstance(assessment, dict) or assessment.get("type") != "deterministic-evidence" or not isinstance(assessment.get("criteria"), list) or not assessment["criteria"]:
        errors.append("assessment must define deterministic-evidence criteria")
    else:
        for criterion in assessment["criteria"]:
            if not isinstance(criterion, dict) or not criterion.get("id") or criterion.get("evidence_id") not in evidence_ids or criterion.get("type") not in {"evidence-present", "field-nonempty", "field-equals"}:
                errors.append("assessment criterion must reference known evidence and a supported type")
            if criterion.get("type") in {"field-nonempty", "field-equals"} and not criterion.get("field"): errors.append("field criterion requires field")
            if criterion.get("type") == "field-equals" and "expected" not in criterion: errors.append("field-equals criterion requires expected")
    learning = definition.get("learning")
    if not isinstance(learning, dict): errors.append("learning must be an object")
    else:
        for key in ["concepts", "techniques", "tools", "vulnerabilities", "defensive_controls", "learning_paths"]:
            if not isinstance(learning.get(key), list): errors.append(f"learning.{key} must be a list")
            elif graph_ids is not None:
                for target in learning[key]:
                    if f"{_learning_kind(key)}:{target}" not in graph_ids: errors.append(f"unknown learning target: {_learning_kind(key)}:{target}")
    return sorted(set(errors)), sorted(set(warnings))


def _learning_kind(key):
    return {"concepts": "concept", "techniques": "technique", "tools": "tool", "vulnerabilities": "vulnerability", "defensive_controls": "defensive-control", "learning_paths": "learning-path"}[key]


def _validate_safety(safety, environment, cleanup):
    errors = []
    if not isinstance(safety, dict): return ["safety must be an object"]
    required = {"scope", "authorized_only", "internet_access", "isolation_required", "host_networking", "privileged", "host_mounts"}
    missing = required - set(safety)
    errors.extend(f"safety missing field: {key}" for key in sorted(missing))
    if safety.get("authorized_only") is not True: errors.append("authorized_only must be true")
    if safety.get("internet_access") is not False: errors.append("internet_access must be false")
    if safety.get("isolation_required") is not True: errors.append("isolation_required must be true")
    for key in ["host_networking", "privileged", "host_mounts"]:
        if safety.get(key) is not False: errors.append(f"{key} must be false")
    if safety.get("scope") != "local-synthetic-fixture": errors.append("scope must be local-synthetic-fixture")
    if not isinstance(environment, dict): errors.append("environment must be an object")
    else:
        if environment.get("type") != "local-fixture": errors.append("environment.type must be local-fixture")
        if environment.get("isolation") != "dedicated-ephemeral": errors.append("environment.isolation must be dedicated-ephemeral")
        if environment.get("network_policy") != "isolated-no-internet": errors.append("environment.network_policy must be isolated-no-internet")
        resources = environment.get("resources")
        if not isinstance(resources, dict): errors.append("environment.resources must be an object")
        else:
            try: cpu_limit = float(resources.get("cpu_limit", 0))
            except (TypeError, ValueError): cpu_limit = 0
            if not 0 < cpu_limit <= 2: errors.append("cpu_limit must be bounded between 0 and 2")
            memory = str(resources.get("memory_limit", ""))
            if not re.fullmatch(r"[1-9][0-9]{0,3}m", memory): errors.append("memory_limit must be a bounded megabyte value")
            if not isinstance(resources.get("pids_limit"), int) or not 16 <= resources["pids_limit"] <= 256: errors.append("pids_limit must be between 16 and 256")
            if not isinstance(resources.get("execution_timeout"), int) or not 1 <= resources["execution_timeout"] <= 600: errors.append("execution_timeout must be between 1 and 600 seconds")
            if resources.get("max_instances") != 1: errors.append("max_instances must be 1")
    if cleanup != {"automatic": True, "reset_supported": True, "retention": "ephemeral"}: errors.append("cleanup must be automatic, resettable, and ephemeral")
    return errors
