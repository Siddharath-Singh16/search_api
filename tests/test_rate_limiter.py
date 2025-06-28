import time
import pytest
from fastapi import HTTPException
from src.core.rate_limiter import enforce_rate_limit, rate_limit_store, RATE_LIMIT, WINDOW_SECONDS, cleanup_rate_limit_store
from collections import deque


@pytest.fixture(autouse=True)
def clear_store_before_test():
    rate_limit_store.clear()
    yield
    rate_limit_store.clear()

def test_allows_requests_under_limit():
    org_id = "test_org"
    for _ in range(RATE_LIMIT - 1):
        enforce_rate_limit(org_id)
    assert org_id in rate_limit_store
    assert len(rate_limit_store[org_id]) == RATE_LIMIT - 1

def test_raises_on_limit_exceeded():
    org_id = "test_org"
    for _ in range(RATE_LIMIT):
        enforce_rate_limit(org_id)
    with pytest.raises(HTTPException) as exc:
        enforce_rate_limit(org_id)
    assert exc.value.status_code == 429

def test_expired_requests_are_cleaned():
    org_id = "test_org"
    old_time = time.time() - (WINDOW_SECONDS + 1)
    rate_limit_store[org_id] = deque([old_time] * RATE_LIMIT)

    enforce_rate_limit(org_id)
    assert len(rate_limit_store[org_id]) == 1  # others should be cleaned


def test_cleanup_removes_empty_orgs():
    org_id = "expired_org"
    old_time = time.time() - (WINDOW_SECONDS + 1)
    rate_limit_store[org_id] = deque([old_time])

    cleanup_rate_limit_store()  # 🔁 This is what actually does the global cleanup

    assert org_id not in rate_limit_store  # ✅ Now this should pass
