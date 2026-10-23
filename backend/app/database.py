import asyncio
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from backend.app.core.config import settings
from backend.app.core.logging import logger

class DatabaseManager:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    _loop = None

    @classmethod
    async def connect_db(cls):
        cls.get_db()

    @classmethod
    async def close_db(cls):
        if cls.client is not None:
            try:
                cls.client.close()
            except Exception:
                pass
            cls.client = None
            cls.db = None
            cls._loop = None

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
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
            if cls.client is not None:
                try:
                    cls.client.close()
                except Exception:
                    pass
            cls._loop = current_loop
            cls.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
                minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
                serverSelectionTimeoutMS=settings.MONGODB_TIMEOUT_MS,
                connectTimeoutMS=settings.MONGODB_TIMEOUT_MS,
                socketTimeoutMS=settings.MONGODB_TIMEOUT_MS
            )
            cls.db = cls.client[settings.MONGODB_DATABASE]

        return cls.db

async def get_db() -> AsyncIOMotorDatabase:
    """FastAPI dependency for accessing database"""
    return DatabaseManager.get_db()
