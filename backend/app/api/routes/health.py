from fastapi import APIRouter, status, Response
from backend.app.database import DatabaseManager
from backend.app.redis_client import RedisManager

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/live")
async def liveness():
    """Liveness probe: verifies process is alive."""
    return {"status": "alive"}

@router.get("/ready")
async def readiness(response: Response):
    """
    Readiness probe: checks MongoDB and Redis connectivity.
    Does not expose connection strings or secrets.
    """
    mongo_ok = False
    redis_ok = False

    # Check MongoDB
    try:
        if DatabaseManager.client is not None:
            await DatabaseManager.client.admin.command("ping")
            mongo_ok = True
    except Exception:
        mongo_ok = False

    # Check Redis
    try:
        client = RedisManager.get_client()
        if client is not None:
            await client.ping()
            redis_ok = True
    except Exception:
        redis_ok = False

    is_ready = mongo_ok  # MongoDB is our primary persistent store; Redis degraded can still respond

    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if is_ready else "not_ready",
        "services": {
            "database": "connected" if mongo_ok else "unreachable",
            "cache_queue": "connected" if redis_ok else "degraded"
        }
    }
