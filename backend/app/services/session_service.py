import json
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from backend.app.core.config import settings
from backend.app.core.security import generate_session_id, hash_session_id
from backend.app.core.logging import logger
from backend.app.redis_client import RedisManager

# In-memory fallback dictionary strictly for testing environments when Redis is offline
_FALLBACK_SESSIONS: Dict[str, Dict[str, Any]] = {}

class SessionService:
    @staticmethod
    def _key(session_hash: str) -> str:
        return f"kg:session:v1:{session_hash}"

    @classmethod
    async def create_session(cls, user_id: str, role: str = "farmer") -> str:
        session_id = generate_session_id()
        session_hash = hash_session_id(session_id)
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=settings.SESSION_TTL_SECONDS)

        session_data = {
            "userId": user_id,
            "role": role,
            "createdAt": now.isoformat(),
            "expiresAt": expires_at.isoformat()
        }

        redis_client = RedisManager.get_client()
        if redis_client is not None:
            try:
                await redis_client.set(
                    cls._key(session_hash),
                    json.dumps(session_data),
                    ex=settings.SESSION_TTL_SECONDS
                )
                logger.info("Session created in Redis", extra={"extra_data": {"user_id": user_id, "role": role}})
                return session_id
            except Exception as e:
                logger.error(f"Failed to store session in Redis: {e}")

        # Fallback for development if Redis connection failed
        _FALLBACK_SESSIONS[session_hash] = session_data
        return session_id

    @classmethod
    async def get_session(cls, session_id: str) -> Optional[Dict[str, Any]]:
        if not session_id:
            return None

        session_hash = hash_session_id(session_id)
        redis_client = RedisManager.get_client()
        
        if redis_client is not None:
            try:
                data = await redis_client.get(cls._key(session_hash))
                if data:
                    return json.loads(data)
                return None
            except Exception as e:
                logger.error(f"Error fetching session from Redis: {e}")

        # Check fallback
        session_data = _FALLBACK_SESSIONS.get(session_hash)
        if session_data:
            expires_at = datetime.fromisoformat(session_data["expiresAt"])
            if expires_at < datetime.now(timezone.utc):
                del _FALLBACK_SESSIONS[session_hash]
                return None
            return session_data

        return None

    @classmethod
    async def revoke_session(cls, session_id: str) -> bool:
        if not session_id:
            return False

        session_hash = hash_session_id(session_id)
        redis_client = RedisManager.get_client()
        revoked = False

        if redis_client is not None:
            try:
                deleted = await redis_client.delete(cls._key(session_hash))
                revoked = bool(deleted > 0)
            except Exception as e:
                logger.error(f"Error revoking session in Redis: {e}")

        if session_hash in _FALLBACK_SESSIONS:
            del _FALLBACK_SESSIONS[session_hash]
            revoked = True

        return revoked
