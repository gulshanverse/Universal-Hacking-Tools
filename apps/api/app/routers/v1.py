"""Versioned routes that adapt generated contracts and existing deterministic engines."""
from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Query, Request, Response

from ..models.contracts import EvidenceSubmission
from ..services.artifacts import artifacts, ENTITY_TYPES
from ..services.labs import labs, LabNotExecutable
from ..services.attempts import begin_attempt, record_assessment
from ..services.rate_limit import LocalRateLimiter
from ..state.database import database_ready
from ..state.auth import optional_mutation_user_id


router = APIRouter(tags=["v1"])
limiter = LocalRateLimiter()


def local_session(response: Response, session: str | None = Cookie(default=None, alias="uht_lab_session"), header_session: str | None = Header(default=None, alias="X-Lab-Session")) -> str:
    import uuid
    value = header_session or session or uuid.uuid4().hex
    if not header_session and not session:
        response.set_cookie("uht_lab_session", value, httponly=True, samesite="strict", secure=False, max_age=3600)
    return value


def expensive(request: Request) -> None:
    limiter.check(f"{request.client.host if request.client else 'local'}:{request.url.path}")


def page(limit: Annotated[int, Query(ge=1, le=100)] = 20, offset: Annotated[int, Query(ge=0)] = 0) -> tuple[int, int]:
    return limit, offset


def entity_or_404(entity_id: str, entity_type: str | None = None) -> dict:
    item = artifacts.resolve(entity_id, entity_type)
    if not item:
        raise HTTPException(status_code=404, detail="entity not found")
    return item


@router.get("/health", summary="API health")
def health():
    artifacts.ensure_ready()
    return {"status": "ok", "version": "8.0.0", "knowledge_version": artifacts.version(), "generated_at": artifacts.generated_at(), "entities": len(artifacts.documents()), "database": "ok" if database_ready() else "degraded"}


@router.get("/ready", summary="Generated-contract readiness")
def ready():
    ok, missing = artifacts.ready()
    if not ok:
        return {"ready": False, "missing": missing, "database": "ok" if database_ready() else "degraded"}
    return {"ready": True, "knowledge_version": artifacts.version(), "required_contracts": list(artifacts.required), "database": "ok" if database_ready() else "degraded", "private_state_available": database_ready()}


@router.get("/health/database", summary="Read private application-state database health without internals")
def database_health():
    if database_ready():
        return {"status": "ok"}
    raise HTTPException(status_code=503, detail="private application state is temporarily unavailable")


@router.get("/knowledge", summary="List normalized knowledge entities")
def knowledge(type: str | None = None, category: str | None = None, difficulty: str | None = None, platform: str | None = None, security_domain: str | None = None, verification_status: str | None = None, confidence: str | None = None, pagination: tuple[int, int] = Depends(page)):
    if type and type not in ENTITY_TYPES:
        raise HTTPException(status_code=422, detail="invalid entity type")
    limit, offset = pagination
    items = artifacts.list_entities(entity_type=type, filters={"category": category, "difficulty": difficulty, "platform": platform, "security_domain": security_domain, "verification_status": verification_status, "confidence": confidence})
    return {"total": len(items), "items": items[offset:offset + limit], "limit": limit, "offset": offset}


@router.get("/knowledge/path", summary="Find a deterministic shortest relationship path")
def knowledge_path(from_: Annotated[str, Query(alias="from", min_length=1)] , to: Annotated[str, Query(min_length=1)], max_depth: Annotated[int, Query(ge=1, le=8)] = 4, _: None = Depends(expensive)):
    found = artifacts.engine("discovery").find_path(from_, to)
    if found and len(found) - 1 > max_depth:
        found = []
    return {"from": from_, "to": to, "found": bool(found), "path": found}


@router.get("/knowledge/{entity_id}", summary="Get one normalized knowledge entity")
def knowledge_detail(entity_id: str):
    return entity_or_404(entity_id)


@router.get("/knowledge/{entity_id}/related", summary="Explore bounded related knowledge")
def related(entity_id: str, depth: Annotated[int, Query(ge=1, le=3)] = 1, limit: Annotated[int, Query(ge=1, le=100)] = 20, relationship_type: str | None = None, entity_type: str | None = None, _: None = Depends(expensive)):
    if entity_type and entity_type not in ENTITY_TYPES:
        raise HTTPException(status_code=422, detail="invalid entity type")
    try:
        return artifacts.related(entity_id, depth, limit, relationship_type, entity_type)
    except ValueError:
        raise HTTPException(status_code=404, detail="entity not found")


@router.get("/knowledge/{entity_id}/recommendations", summary="Get deterministic learning recommendations")
def recommendations(entity_id: str, difficulty: str | None = None, goal: str | None = None, limit: Annotated[int, Query(ge=1, le=50)] = 10, _: None = Depends(expensive)):
    try:
        return artifacts.engine("recommendation").recommend(entity_id, difficulty=difficulty, goals=[goal] if goal else [], limit=limit)
    except ValueError:
        raise HTTPException(status_code=404, detail="entity not found")


@router.get("/search", summary="Search deterministic generated knowledge")
def search(q: str = "", type: str | None = None, category: str | None = None, subcategory: str | None = None, difficulty: str | None = None, platform: str | None = None, security_domain: str | None = None, license: str | None = None, dual_use: str | None = None, verification_status: str | None = None, confidence: str | None = None, pagination: tuple[int, int] = Depends(page), _: None = Depends(expensive)):
    if type and type not in ENTITY_TYPES:
        raise HTTPException(status_code=422, detail="invalid entity type")
    limit, offset = pagination
    return artifacts.search(q, limit, offset, {"type": type, "category": category, "subcategory": subcategory, "difficulty": difficulty, "platform": platform, "security_domain": security_domain, "license": license, "dual_use": dual_use, "verification_status": verification_status, "confidence": confidence})


@router.get("/compare", summary="Compare known tool metadata without benchmarks")
def compare(a: Annotated[str, Query(min_length=1)], b: Annotated[str, Query(min_length=1)]):
    try:
        return artifacts.engine("comparison").compare(a, b)
    except ValueError:
        raise HTTPException(status_code=404, detail="tool not found")


def type_routes(prefix: str, entity_type: str):
    @router.get(f"/{prefix}", summary=f"List {prefix}")
    def list_type(pagination: tuple[int, int] = Depends(page)):
        limit, offset = pagination
        items = artifacts.list_entities(entity_type=entity_type)
        return {"total": len(items), "items": items[offset:offset + limit], "limit": limit, "offset": offset}

    @router.get(f"/{prefix}/{{entity_id}}", summary=f"Get one {entity_type}")
    def detail_type(entity_id: str):
        return entity_or_404(entity_id, entity_type)


for _prefix, _type in (("tools", "tool"), ("vulnerabilities", "vulnerability"), ("concepts", "concept"), ("techniques", "technique"), ("technologies", "technology"), ("defensive-controls", "defensive-control"), ("learning-paths", "learning-path")):
    type_routes(_prefix, _type)


@router.get("/trust", summary="Read transparent aggregate trust report")
def trust():
    report = artifacts.json("trust-report.json")
    return {key: value for key, value in report.items() if key != "entity_trust"}


@router.get("/trust/{entity_id}", summary="Read trust details for one entity")
def entity_trust(entity_id: str):
    entity = entity_or_404(entity_id)
    key = f"{entity['type']}:{entity['id']}"
    item = next((row for row in artifacts.json("trust-report.json").get("entity_trust", []) if row.get("entity") == key), None)
    if not item:
        raise HTTPException(status_code=404, detail="entity trust entry not found")
    return item


@router.get("/health/knowledge", summary="Read generated knowledge health")
def knowledge_health():
    return artifacts.json("knowledge-health.json")


@router.get("/health/labs", summary="Read generated lab health")
def lab_health():
    return artifacts.json("lab-health.json")


@router.get("/review/queue", summary="Read-only deterministic review queue")
def review_queue(pagination: tuple[int, int] = Depends(page)):
    limit, offset = pagination
    payload = artifacts.json("review-queue.json")
    items = payload.get("items", [])
    return {"as_of": payload.get("as_of"), "total": len(items), "items": items[offset:offset + limit], "limit": limit, "offset": offset}


@router.get("/review/{entity_id}", summary="Read one review item")
def review_item(entity_id: str):
    entity = entity_or_404(entity_id)
    key = f"{entity['type']}:{entity['id']}"
    item = next((row for row in artifacts.json("review-queue.json").get("items", []) if row.get("entity") == key), None)
    if not item:
        raise HTTPException(status_code=404, detail="review item not found")
    return item


@router.get("/labs", summary="List safe lab metadata")
def list_labs(pagination: tuple[int, int] = Depends(page)):
    limit, offset = pagination
    items = artifacts.labs()
    return {"total": len(items), "items": items[offset:offset + limit], "limit": limit, "offset": offset}


@router.get("/labs/{lab_id}", summary="Get safe lab metadata")
def lab_detail(lab_id: str):
    item = artifacts.lab(lab_id)
    if not item:
        raise HTTPException(status_code=404, detail="lab not found")
    return item


@router.post("/labs/{lab_id}/instances", summary="Create an approved local-fixture lab instance")
def create_instance(lab_id: str, response: Response, dry_run: bool = False, session_id: str = Depends(local_session), authenticated_session: str | None = Cookie(default=None, alias="uht_session"), csrf_cookie: str | None = Cookie(default=None, alias="uht_csrf"), csrf_header: str | None = Header(default=None, alias="X-CSRF-Token"), _: None = Depends(expensive)):
    user_id = optional_mutation_user_id(authenticated_session, csrf_cookie, csrf_header)
    result = labs.create(lab_id, session_id, dry_run=dry_run)
    if not dry_run:
        begin_attempt(user_id, lab_id)
    return result


@router.get("/lab-instances/{instance_id}", summary="Read a local lab instance status")
def instance_status(instance_id: str, response: Response, session_id: str = Depends(local_session)):
    return labs.status(instance_id, session_id)


@router.post("/lab-instances/{instance_id}/start", summary="Start a safe local lab instance")
def start_instance(instance_id: str, response: Response, session_id: str = Depends(local_session)):
    return labs.transition(instance_id, session_id, "start")


@router.post("/lab-instances/{instance_id}/stop", summary="Stop a safe local lab instance")
def stop_instance(instance_id: str, response: Response, session_id: str = Depends(local_session)):
    return labs.transition(instance_id, session_id, "stop")


@router.post("/lab-instances/{instance_id}/reset", summary="Reset a safe local lab instance and clear evidence")
def reset_instance(instance_id: str, response: Response, session_id: str = Depends(local_session)):
    return labs.transition(instance_id, session_id, "reset")


@router.delete("/lab-instances/{instance_id}", summary="Destroy a safe local lab instance and clear ephemeral state")
def destroy_instance(instance_id: str, response: Response, session_id: str = Depends(local_session)):
    return labs.destroy(instance_id, session_id)


@router.post("/lab-instances/{instance_id}/tasks/{task_id}/run", summary="Run one predefined local-fixture task")
def run_task(instance_id: str, task_id: str, response: Response, session_id: str = Depends(local_session)):
    return labs.run_task(instance_id, session_id, task_id)


@router.get("/lab-instances/{instance_id}/evidence", summary="Read structured local lab evidence")
def evidence(instance_id: str, response: Response, session_id: str = Depends(local_session)):
    return labs.evidence(instance_id, session_id)


@router.post("/lab-instances/{instance_id}/evidence", summary="Submit bounded structured evidence for an approved task")
def submit_evidence(instance_id: str, payload: EvidenceSubmission, response: Response, session_id: str = Depends(local_session)):
    return labs.submit_evidence(instance_id, session_id, payload.task_id, payload.evidence_id, payload.value)


@router.get("/lab-instances/{instance_id}/assessment", summary="Read deterministic lab assessment")
def assessment(instance_id: str, response: Response, session_id: str = Depends(local_session), _: None = Depends(expensive)):
    return labs.assess(instance_id, session_id)


@router.post("/lab-instances/{instance_id}/assessment/record", summary="Persist only a minimal authenticated safe-lab assessment summary")
def record_assessment_result(instance_id: str, response: Response, session_id: str = Depends(local_session), authenticated_session: str | None = Cookie(default=None, alias="uht_session"), csrf_cookie: str | None = Cookie(default=None, alias="uht_csrf"), csrf_header: str | None = Header(default=None, alias="X-CSRF-Token"), _: None = Depends(expensive)):
    user_id = optional_mutation_user_id(authenticated_session, csrf_cookie, csrf_header)
    if not user_id:
        raise HTTPException(status_code=401, detail="authentication is required to save lab history")
    result = labs.assess(instance_id, session_id)
    result["new_achievements"] = record_assessment(user_id, result)
    return result
