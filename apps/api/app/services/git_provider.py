"""Server-only Git handoff boundary. The web API never executes Git or exposes credentials."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class HandoffResult:
    status: str  # queued | failed | created
    message: str
    pull_request_url: str | None = None
    commit_sha: str | None = None


class GitProvider(Protocol):
    def create_pull_request(self, *, contribution_id: str, branch: str, files: list[dict[str, str]], title: str, body: str) -> HandoffResult: ...


class UnavailableGitProvider:
    """Safe default when a server-side GitHub App/token is not configured."""
    def create_pull_request(self, *, contribution_id: str, branch: str, files: list[dict[str, str]], title: str, body: str) -> HandoffResult:
        return HandoffResult("failed", "Git provider handoff is not configured; use the documented manual pull-request workflow.")


class MockGitProvider:
    """Deterministic test adapter; never contacts GitHub."""
    def __init__(self, outcome: str = "created"):
        self.outcome = outcome

    def create_pull_request(self, *, contribution_id: str, branch: str, files: list[dict[str, str]], title: str, body: str) -> HandoffResult:
        if self.outcome == "created":
            return HandoffResult("created", "Mock pull request created for test validation.", f"https://example.test/pull/{contribution_id}", "0" * 40)
        if self.outcome == "queued":
            return HandoffResult("queued", "Mock handoff is queued for test validation.")
        return HandoffResult("failed", f"Mock Git provider failure: {self.outcome}.")
