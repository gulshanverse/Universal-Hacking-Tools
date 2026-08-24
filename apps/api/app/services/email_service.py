"""Injectable, non-network email boundary for verification and reset notices."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PendingEmail:
    recipient: str
    purpose: str
    token: str


class DevelopmentEmailService:
    """Stores test/development messages in memory; never logs sensitive tokens."""

    def __init__(self) -> None:
        self._outbox: list[PendingEmail] = []

    def send_verification(self, recipient: str, token: str) -> None:
        self._outbox.append(PendingEmail(recipient, "verify-email", token))

    def send_password_reset(self, recipient: str, token: str) -> None:
        self._outbox.append(PendingEmail(recipient, "password-reset", token))

    def latest(self, recipient: str, purpose: str) -> PendingEmail | None:
        return next((item for item in reversed(self._outbox) if item.recipient == recipient and item.purpose == purpose), None)

    def clear(self) -> None:
        self._outbox.clear()


email_service = DevelopmentEmailService()
