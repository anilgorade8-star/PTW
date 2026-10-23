import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.app.core.config import settings
from backend.app.core.errors import NotFoundError, AuthorizationError, ValidationError
from backend.app.core.logging import logger
from backend.app.repositories.assessment_repo import AssessmentRepository
from backend.app.repositories.farm_repo import FarmRepository
from backend.app.repositories.weather_repo import WeatherRepository
from backend.app.services.storage_service import storage_service
from backend.app.services.weather_service import WeatherService
from backend.app.services.gemini_service import GeminiService
from backend.app.services.knowledge_service import KnowledgeService
from backend.app.decision_engine import DecisionEngine
from backend.app.queue import AssessmentQueue
from backend.app.redis_client import RedisManager

class AssessmentService:
    @classmethod
    async def create_assessment(
        cls,
        db: AsyncIOMotorDatabase,
        owner_user_id: str,
        farm_id: str,
        crop_type: str,
        growth_stage: str,
        image_bytes: bytes,
        filename: str,
        reported_symptoms: List[str],
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validates ownership, saves image, creates assessment in MongoDB, and dispatches to queue.
        """
        # 1. Idempotency check with Redis if provided
        redis_client = RedisManager.get_client()
        if redis_client is not None and idempotency_key:
            idem_key = f"kg:idem:assessment:{owner_user_id}:{idempotency_key}"
            is_new = await redis_client.set(idem_key, "1", nx=True, ex=300)
            if not is_new:
                raise ValidationError("Duplicate submission detected. An identical request is already being processed.")

        # 2. Enforce farm ownership server-side
        farm_repo = FarmRepository(db)
        farm = await farm_repo.get_by_id(farm_id)
        if not farm:
            raise NotFoundError("Farm", farm_id)
        if str(farm["ownerUserId"]) != owner_user_id:
            raise AuthorizationError("You do not own this farm.")

        # 3. Validate and store image
        storage_key, relative_url = storage_service.validate_and_save_image(image_bytes, filename)

        # 4. Insert assessment record into MongoDB
        assessment_repo = AssessmentRepository(db)
        assessment = await assessment_repo.create_assessment(
            owner_user_id=owner_user_id,
            farm_id=farm_id,
            crop_type=crop_type,
            growth_stage=growth_stage,
            image_key=storage_key,
            farmer_reported_symptoms=reported_symptoms
        )
        assessment_id = str(assessment["_id"])

        # 5. Dispatch to background worker
        dispatched = AssessmentQueue.dispatch_assessment(assessment_id)
        if not dispatched:
            # Fallback: schedule background execution within the current event loop
            logger.warning("Queue dispatch unavailable, executing assessment asynchronously in background task")
            asyncio.create_task(cls.run_pipeline(assessment_id, db))

        return assessment

    @classmethod
    async def run_pipeline(cls, assessment_id: str, db: AsyncIOMotorDatabase):
        """
        The Farm Evidence Loop execution pipeline:
        Fetch context -> Weather -> Image analysis (Gemini) -> Knowledge retrieval -> Decision engine -> Persistence.
        """
        assessment_repo = AssessmentRepository(db)
        farm_repo = FarmRepository(db)
        weather_repo = WeatherRepository(db)

        assessment = await assessment_repo.get_by_id(assessment_id)
        if not assessment:
            logger.error(f"Assessment {assessment_id} not found in pipeline.")
            return

        try:
            await assessment_repo.update_status(assessment_id, "processing")
            logger.info(f"Processing assessment {assessment_id} in Farm Evidence Loop...")

            # 1. Fetch farm coordinates
            farm = await farm_repo.get_by_id(str(assessment["farmId"]))
            lat = 20.5937
            lon = 78.9629
            if farm and "location" in farm:
                loc = farm["location"]
                lat = float(loc.get("latitude", lat))
                lon = float(loc.get("longitude", lon))

            # 2. Fetch and cache weather
            normalized_weather, quality_meta = await WeatherService.get_farm_weather(lat, lon)
            snapshot = await weather_repo.save_snapshot(
                farm_id=str(assessment["farmId"]),
                provider=quality_meta.get("provider", "open-meteo"),
                normalized_data=normalized_weather,
                quality_metadata=quality_meta
            )
            weather_snapshot_id = snapshot["_id"]

            # 3. Read image for Gemini AI analysis
            img_path = storage_service.get_image_path(assessment["imageStorageKey"])
            if not img_path:
                raise ValidationError("Assessment crop image file is missing on server.")

            with open(img_path, "rb") as f:
                img_bytes = f.read()

            # 4. Gemini structured visual symptom observation
            visual_analysis = await GeminiService.analyze_crop_image(
                image_bytes=img_bytes,
                crop_type=assessment.get("cropType", "tomato"),
                growth_stage=assessment.get("growthStage", "vegetative"),
                reported_symptoms=assessment.get("farmerReportedSymptoms", [])
            )

            # 5. Retrieve reviewed agricultural knowledge sources
            knowledge_sources = await KnowledgeService.get_all_sources(db)

            # 6. Deterministic Decision Engine
            decision_result = DecisionEngine.evaluate(
                visual_analysis=visual_analysis,
                reported_symptoms=assessment.get("farmerReportedSymptoms", []),
                crop_type=assessment.get("cropType", "tomato"),
                growth_stage=assessment.get("growthStage", "vegetative"),
                weather=normalized_weather,
                knowledge_sources=knowledge_sources
            )

            # 7. Check if assessment is awaiting farmer input or completed
            final_status = "awaiting_farmer_input" if decision_result.needsFarmerInput else "completed"

            # 8. Persist results to MongoDB
            await assessment_repo.save_results(
                assessment_id=assessment_id,
                observations=visual_analysis.visible_symptoms,
                candidate_explanations=[c.model_dump() for c in decision_result.candidateExplanations],
                decision=decision_result.model_dump(),
                safety_review=decision_result.safetyReview.model_dump(),
                source_references=[s.model_dump() for s in decision_result.sourceReferences],
                weather_snapshot_id=weather_snapshot_id,
                status=final_status
            )

            logger.info(
                f"Assessment {assessment_id} pipeline finished successfully with status: {final_status}",
                extra={"extra_data": {"primary_condition": decision_result.primaryCondition, "certainty": decision_result.certaintyLevel}}
            )

        except Exception as e:
            logger.error(f"Assessment {assessment_id} pipeline failed: {e}", exc_info=True)
            await assessment_repo.update_status(assessment_id, "failed", failure_code=str(e))
