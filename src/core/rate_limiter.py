import time
import logging
from collections import deque, defaultdict
from fastapi import HTTPException
from typing import Dict, Deque

logger = logging.getLogger(__name__)

RATE_LIMIT = 20
WINDOW_SECONDS = 60
MAX_ORGS = 10000

class RateLimiter:
    def __init__(self, rate_limit: int = RATE_LIMIT, window_seconds: int = WINDOW_SECONDS):
        self.rate_limit = rate_limit
        self.window_seconds = window_seconds
        self._store: Dict[str, Deque[float]] = defaultdict(deque)
        self._last_cleanup = time.time()
    
    def enforce(self, org_id: str) -> None:
        """
        Enforce rate limiting for the given organization ID.
        
        Args:
            org_id: Organization ID to check
            
        Raises:
            HTTPException: If rate limit is exceeded
        """
        try:
            now = time.time()
            
            if len(self._store) > MAX_ORGS or (now - self._last_cleanup > 300):
                self.cleanup()
            
            window = self._store[org_id]
            
            while window and now - window[0] > self.window_seconds:
                window.popleft()
            
            if len(window) >= self.rate_limit:
                logger.warning(f"Rate limit exceeded for org_id={org_id}, requests={len(window)}")
                raise HTTPException(
                    status_code=429, 
                    detail=f"Rate limit exceeded. Maximum {self.rate_limit} requests per {self.window_seconds} seconds."
                )
            
            window.append(now)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in rate limiter: {str(e)}")
            try:
                self._store[org_id].append(now)
            except:
                pass

    def cleanup(self) -> None:
        """
        Remove expired timestamps and empty organization entries.
        Should be called periodically to prevent memory leaks.
        """
        try:
            now = time.time()
            self._last_cleanup = now
            
            expired_keys = []
            count_before = len(self._store)
            
            for org_id, timestamps in self._store.items():
                try:
                    while timestamps and now - timestamps[0] > self.window_seconds:
                        timestamps.popleft()
                    
                    if not timestamps:
                        expired_keys.append(org_id)
                except Exception as e:
                    logger.error(f"Error cleaning up timestamps for org_id={org_id}: {str(e)}")
            
            for org_id in expired_keys:
                try:
                    del self._store[org_id]
                except Exception as e:
                    logger.error(f"Error removing org_id={org_id} from store: {str(e)}")
            
            count_after = len(self._store)
            if count_before != count_after:
                logger.info(f"Rate limiter cleanup: removed {count_before - count_after} organizations")
                
        except Exception as e:
            logger.error(f"Error during rate limiter cleanup: {str(e)}")

    def reset(self) -> None:
        """
        Reset the rate limiter state. Primarily used for testing.
        """
        try:
            self._store.clear()
            self._last_cleanup = time.time()
        except Exception as e:
            logger.error(f"Error resetting rate limiter: {str(e)}")

rate_limiter = RateLimiter()
