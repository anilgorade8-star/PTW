from typing import Callable
from fastapi import Request
from backend.app.redis_client import RedisManager
from backend.app.core.errors import RateLimitExceededError

def rate_limit(endpoint_name: str, max_requests: int, window_seconds: int) -> Callable:
    async def _checker(request: Request):
        # Determine client identifier: IP address or session user
        client_ip = request.client.host if request.client else "unknown"
        # Optional: check if forward header is present from trusted proxy
        key = f"kg:rl:{endpoint_name}:{client_ip}"
        
        allowed, remaining, retry_after = await RedisManager.check_rate_limit(
            key=key,
            max_limit=max_requests,
            window_seconds=window_seconds
        )

        if not allowed:
            raise RateLimitExceededError(retry_after=retry_after)

    return _checker
