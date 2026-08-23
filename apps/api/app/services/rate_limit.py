"""Small process-local rate limiter; no telemetry, persistence, or external services."""
from collections import defaultdict, deque
from time import monotonic


class RateLimitExceeded(RuntimeError):
    pass


class LocalRateLimiter:
    def __init__(self, limit: int = 60, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        self._buckets: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> None:
        now = monotonic()
        bucket = self._buckets[key]
        while bucket and bucket[0] <= now - self.window_seconds:
            bucket.popleft()
        if len(bucket) >= self.limit:
            raise RateLimitExceeded("rate limit exceeded; retry shortly")
        bucket.append(now)
