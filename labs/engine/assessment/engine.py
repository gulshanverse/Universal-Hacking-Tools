"""Deterministic, rubric-driven assessment; no model or external service is used."""


def _field(value, path):
    current = value
    for part in str(path).split("."):
        if isinstance(current, dict): current = current.get(part)
        else: return None
    return current


def _nonempty(value):
    return value is not None and value != "" and value != [] and value != {}


def assess(definition, evidence_records):
    by_id = {}
    for item in evidence_records:
        by_id.setdefault(item.get("evidence_id"), []).append(item.get("value"))
    results = []
    for criterion in definition.get("assessment", {}).get("criteria", []):
        values = by_id.get(criterion.get("evidence_id"), [])
        passed = False
        if criterion.get("type") == "evidence-present":
            passed = bool(values)
        elif criterion.get("type") == "field-nonempty":
            passed = any(_nonempty(_field(value, criterion.get("field"))) for value in values)
        elif criterion.get("type") == "field-equals":
            passed = any(_field(value, criterion.get("field")) == criterion.get("expected") for value in values)
        results.append({"criterion_id": criterion.get("id"), "evidence_id": criterion.get("evidence_id"), "status": "passed" if passed else "failed", "feedback": "Criterion satisfied." if passed else criterion.get("feedback", "Provide the required evidence.")})
    total = len(results)
    passed = sum(1 for item in results if item["status"] == "passed")
    if not evidence_records: status = "not-started"
    elif passed == total and total: status = "passed"
    elif passed: status = "partial"
    else: status = "failed"
    return {"lab_id": definition.get("id"), "status": status, "passed_criteria": passed, "total_criteria": total, "criteria": results, "feedback": "All rubric criteria satisfied." if status == "passed" else "Review the criterion feedback and collect only the evidence required by the lab rubric."}
