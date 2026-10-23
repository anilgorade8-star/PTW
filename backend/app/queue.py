import os
import asyncio
from typing import Optional
from redis import Redis
from rq import Queue, Retry
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.redis_client import RedisManager

QUEUE_NAME = "krishiguard_assessments"

class AssessmentQueue:
    _sync_redis: Optional[Redis] = None
    _queue: Optional[Queue] = None

    @classmethod
    def get_queue(cls) -> Optional[Queue]:
        if cls._queue is None:
            try:
                cls._sync_redis = Redis.from_url(
                    settings.REDIS_URL,
                    socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                    socket_connect_timeout=settings.REDIS_CONNECT_TIMEOUT
                )
                cls._sync_redis.ping()
                cls._queue = Queue(QUEUE_NAME, connection=cls._sync_redis)
                logger.info(f"RQ queue '{QUEUE_NAME}' initialized successfully.")
            except Exception as e:
                logger.warning(f"Could not connect to Redis for RQ queue: {e}")
                cls._queue = None
        return cls._queue

    @classmethod
    def dispatch_assessment(cls, assessment_id: str) -> bool:
        """
        Dispatches assessment ID to RQ background worker.
        Returns True if enqueued, False if Redis queue failed (outbox pattern needed).
        """
        q = cls.get_queue()
        if q is None:
            return False

        try:
            # Enqueue with 3 retries, exponential backoff, and 180s job timeout
            job = q.enqueue(
                "backend.worker.execute_assessment_job",
                assessment_id,
                job_timeout=settings.ASSESSMENT_JOB_TIMEOUT_SECONDS,
                retry=Retry(max=3, interval=[5, 15, 30]),
                job_id=f"assessment:{assessment_id}"
            )
            logger.info("Assessment enqueued to RQ worker", extra={"extra_data": {"job_id": job.id, "assessment_id": assessment_id}})
            return True
        except Exception as e:
            logger.error(f"Failed to enqueue assessment to RQ: {e}")
            return False
