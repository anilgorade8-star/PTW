import pytest
import pytest_asyncio
import httpx
from backend.app.main import app
from backend.app.database import DatabaseManager
from backend.app.redis_client import RedisManager

@pytest_asyncio.fixture(autouse=True)
async def clear_rate_limits_for_tests():
    await DatabaseManager.connect_db()
    await RedisManager.connect_redis()
    client = RedisManager.get_client()
    if client is not None:
        try:
            keys = await client.keys("kg:rl:*")
            if keys:
                await client.delete(*keys)
        except Exception:
            pass
    yield

@pytest_asyncio.fixture
async def client():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver"
    ) as ac:
        yield ac
