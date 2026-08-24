"""Thin Phase 7 adapter over the Phase 6 lifecycle manager; never executes arbitrary commands."""
from __future__ import annotations
from pathlib import Path
import os

from labs.engine.lifecycle.manager import LabManager
from .artifacts import artifacts
from ..state.config import settings


class LabNotExecutable(ValueError):
    pass


class LabService:
    def __init__(self):
        self._manager: LabManager | None = None
        self._sessions: dict[str, set[str]] = {}

    @property
    def manager(self) -> LabManager:
        root = Path(settings().lab_state_dir)
        if self._manager is None or self._manager.state_root != root.resolve():
            self._manager = LabManager(root)
            self._sessions = {}
        return self._manager

    def _assert_executable(self, lab_id: str) -> dict:
        lab = artifacts.lab(lab_id)
        if not lab:
            raise ValueError("unknown lab")
        if lab.get("execution_mode") != "executable" or not lab.get("safety_valid"):
            raise LabNotExecutable("lab is not an approved executable local-fixture lab")
        return lab

    def create(self, lab_id: str, session_id: str, dry_run: bool = False) -> dict:
        self._assert_executable(lab_id)
        manager = self.manager
        active = self._sessions.setdefault(session_id, set())
        if not dry_run and active:
            raise ValueError("maximum active lab instances reached for this local session")
        result = manager.create(lab_id, dry_run=dry_run)
        if not dry_run:
            active.add(result["instance_id"])
        return result

    def status(self, instance_id: str, session_id: str) -> dict:
        self._require_session(instance_id, session_id)
        return self.manager.status(instance_id)

    def transition(self, instance_id: str, session_id: str, operation: str) -> dict:
        self._require_session(instance_id, session_id)
        return getattr(self.manager, operation)(instance_id)

    def run_task(self, instance_id: str, session_id: str, task_id: str) -> dict:
        self._require_session(instance_id, session_id)
        return self.manager.run_task(instance_id, task_id)

    def evidence(self, instance_id: str, session_id: str) -> dict:
        self._require_session(instance_id, session_id)
        return self.manager.evidence(instance_id)

    def submit_evidence(self, instance_id: str, session_id: str, task_id: str, evidence_id: str, value: object) -> dict:
        self._require_session(instance_id, session_id)
        return self.manager.submit_evidence(instance_id, task_id, evidence_id, value)

    def assess(self, instance_id: str, session_id: str) -> dict:
        self._require_session(instance_id, session_id)
        return self.manager.assess(instance_id)

    def destroy(self, instance_id: str, session_id: str) -> dict:
        self._require_session(instance_id, session_id)
        result = self.manager.destroy(instance_id)
        self._sessions.get(session_id, set()).discard(instance_id)
        return result

    def _require_session(self, instance_id: str, session_id: str) -> None:
        if instance_id not in self._sessions.get(session_id, set()):
            raise ValueError("unknown lab instance for this local session")


labs = LabService()
