"""
backend/worker.py — Background RQ Worker for KrishiGuard AI
"""
import sys
import asyncio
from pathlib import Path
from redis import Redis
from rq import Worker, Queue, Connection
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.database import DatabaseManager

def execute_assessment_job(assessment_id: str):
    """Sync wrapper executed by RQ worker that runs the async pipeline"""
    logger.info(f"[RQ WORKER] Executing assessment job: {assessment_id}")
    
    async def _async_run():
        await DatabaseManager.connect_db()
        from backend.app.services.assessment_service import AssessmentService
        db = DatabaseManager.get_db()
        await AssessmentService.run_pipeline(assessment_id, db)
        await DatabaseManager.close_db()

    asyncio.run(_async_run())

def start_worker():
    """Start listening to the assessment queue"""
    logger.info("Starting KrishiGuard RQ worker process...")
    redis_conn = Redis.from_url(settings.REDIS_URL)
    with Connection(redis_conn):
        worker = Worker(["krishiguard_assessments"])
        worker.work(with_scheduler=True)

if __name__ == "__main__":
    start_worker()
