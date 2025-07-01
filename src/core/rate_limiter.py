import time
from collections import deque, defaultdict
from fastapi import HTTPException

RATE_LIMIT = 20  # requests per minute per org
WINDOW_SECONDS = 60

class RateLimiter:
    def __init__(self, rate_limit: int = RATE_LIMIT, window_seconds: int = WINDOW_SECONDS):
        self.rate_limit = rate_limit
        self.window_seconds = window_seconds
        self._store = defaultdict(deque) 

    def enforce(self, org_id: str):
        now = time.time()
        window = self._store[org_id]

        while window and now - window[0] > self.window_seconds:
            window.popleft()

        if len(window) >= self.rate_limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        window.append(now)

    def cleanup(self):
        now = time.time()
        expired_keys = []
        for org_id, timestamps in self._store.items():
            while timestamps and now - timestamps[0] > self.window_seconds:
                timestamps.popleft()
            if not timestamps:
                expired_keys.append(org_id)
        for org_id in expired_keys:
            del self._store[org_id]

    def reset(self):
        self._store.clear()

rate_limiter = RateLimiter()
