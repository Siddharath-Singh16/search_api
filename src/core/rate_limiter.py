import time
from collections import deque
from fastapi import HTTPException

RATE_LIMIT = 20
WINDOW_SECONDS = 60

rate_limit_store = {}

def enforce_rate_limit(org_id: str):
    now = time.time()
    window = rate_limit_store.get(org_id, deque())

    while window and now - window[0] > WINDOW_SECONDS:
        window.popleft()

    if not window:
        rate_limit_store.pop(org_id, None)
    else:
        rate_limit_store[org_id] = window

    if len(window) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    window.append(now)
    rate_limit_store[org_id] = window

def cleanup_rate_limit_store():
    now = time.time()
    expired_keys = []
    for org_id, timestamps in rate_limit_store.items():
        while timestamps and now - timestamps[0] > WINDOW_SECONDS:
            timestamps.popleft()
        if not timestamps:
            expired_keys.append(org_id)
    for org_id in expired_keys:
        rate_limit_store.pop(org_id, None)