import asyncio
import time
from typing import Optional, Tuple
import redis.asyncio as aioredis
from redis.exceptions import RedisError
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.core.errors import RateLimitExceededError

SLIDING_WINDOW_LUA = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])

local clearBefore = now - window
redis.call('ZREMRANGEBYSCORE', key, 0, clearBefore)
local currentRequests = redis.call('ZCARD', key)

if currentRequests < limit then
    redis.call('ZADD', key, now, now .. '-' .. math.random(1, 1000000))
    redis.call('EXPIRE', key, window + 1)
    return {1, limit - currentRequests - 1, 0}
else
    local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
    local retryAfter = 1
    if #oldest >= 2 then
        retryAfter = math.ceil(tonumber(oldest[2]) + window - now)
        if retryAfter < 1 then retryAfter = 1 end
    end
    return {0, 0, retryAfter}
end
"""

class RedisManager:
    client: Optional[aioredis.Redis] = None
    rate_limit_script = None
    _loop = None

    @classmethod
    async def connect_redis(cls):
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        is_stale = (
            cls.client is None or
            cls._loop != current_loop or
            (cls._loop is not None and getattr(cls._loop, "is_closed", lambda: False)())
        )

        if is_stale:
            cls._loop = current_loop
            try:
                cls.client = aioredis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                    socket_connect_timeout=settings.REDIS_CONNECT_TIMEOUT
                )
                cls.rate_limit_script = cls.client.register_script(SLIDING_WINDOW_LUA)
            except Exception as e:
                logger.error(f"Redis connection failed: {e}")
                cls.client = None

    @classmethod
    async def close_redis(cls):
        if cls.client is not None:
            try:
                await cls.client.aclose()
            except Exception:
                pass
            cls.client = None
            cls._loop = None

    @classmethod
    def get_client(cls) -> Optional[aioredis.Redis]:
        return cls.client

    @classmethod
    async def check_rate_limit(cls, key: str, max_limit: int, window_seconds: int) -> Tuple[bool, int, int]:
        await cls.connect_redis()
        if cls.client is None or cls.rate_limit_script is None:
            return (True, max_limit, 0)

        now = time.time()
        try:
            result = await cls.rate_limit_script(
                keys=[key],
                args=[now, window_seconds, max_limit]
            )
            allowed = bool(result[0] == 1)
            remaining = int(result[1])
            retry_after = int(result[2])
            return (allowed, remaining, retry_after)
        except RedisError as e:
            logger.error(f"Redis rate limit script error: {e}")
            return (True, max_limit, 0)

async def get_redis() -> Optional[aioredis.Redis]:
    return RedisManager.get_client()
