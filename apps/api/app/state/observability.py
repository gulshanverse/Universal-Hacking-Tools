"""Minimal structured, privacy-aware API observability helpers."""
from __future__ import annotations

import json
import logging
import re
import sys
from datetime import datetime, timezone
from time import perf_counter
from typing import Any
from uuid import uuid4


REQUEST_ID = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


def request_id(value: str | None) -> str:
    return value if value and REQUEST_ID.fullmatch(value) else uuid4().hex


def duration_ms(start: float) -> int:
    return int((perf_counter() - start) * 1000)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {"timestamp": datetime.now(timezone.utc).isoformat(), "level": record.levelname, "service": "api", "event": getattr(record, "event", "log"), "message": record.getMessage()}
        for key in ("request_id", "route", "method", "status", "duration_ms", "environment"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def configure_logging(level: str) -> logging.Logger:
    logger = logging.getLogger("uht.api")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False
    if not any(getattr(handler, "_uht_structured", False) for handler in logger.handlers):
        handler = logging.StreamHandler(sys.stdout)
        handler._uht_structured = True  # type: ignore[attr-defined]
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    return logger
