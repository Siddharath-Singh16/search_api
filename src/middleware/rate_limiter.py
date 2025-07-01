import time
from collections import deque, defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import threading

RATE_LIMIT = 20
WINDOW_SECONDS = 60

rate_limiter_instance = None

class RateLimiterMiddleware(BaseHTTPMiddleware):
    
    def __init__(self, app, rate_limit: int = RATE_LIMIT, window_seconds: int = WINDOW_SECONDS):
        super().__init__(app)
        self._store = defaultdict(deque)
        self._lock = threading.RLock()
        self.rate_limit = rate_limit
        self.window_seconds = window_seconds
        global rate_limiter_instance
        rate_limiter_instance = self

    async def dispatch(self, request: Request, call_next):
        org_id = request.query_params.get("org_id")
        now = time.time()
        
        with self._lock:
            timestamps = self._store[org_id]

            while timestamps and now - timestamps[0] > self.window_seconds:
                timestamps.popleft()

            if len(timestamps) >= self.rate_limit:
                raise HTTPException(
                    status_code=429, 
                    detail=f"Rate limit exceeded. Maximum {self.rate_limit} requests per {self.window_seconds} seconds.",
                    headers={"Retry-After": str(self.window_seconds)}
                )

            timestamps.append(now)

        response = await call_next(request)
        return response
    
    def reset(self, org_id: str = None):
        """Reset the rate limiter state. Used primarily for testing."""
        with self._lock:
            if org_id:
                if org_id in self._store:
                    del self._store[org_id]
            else:
                self._store.clear()
    
    def get_remaining_requests(self, org_id: str) -> int:
        """Get the number of remaining requests for an org_id"""
        if not org_id:
            return 0
            
        now = time.time()
        with self._lock:
            timestamps = self._store[org_id]
            
            while timestamps and now - timestamps[0] > self.window_seconds:
                timestamps.popleft()
            
            return max(0, self.rate_limit - len(timestamps))
    
    def get_reset_time(self, org_id: str) -> float:
        """Get the time when the rate limit will reset for an org_id"""
        if not org_id:
            return time.time()
            
        with self._lock:
            timestamps = self._store[org_id]
            if not timestamps:
                return time.time()
            return timestamps[0] + self.window_seconds