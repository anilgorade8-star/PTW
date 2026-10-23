from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.app.core.errors import NotFoundError, AuthorizationError

class AssessmentRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.assessments = db.assessments
        self.followups = db.followups

    async def create_assessment(
        self,
        owner_user_id: str,
        farm_id: str,
        crop_type: str,
        growth_stage: str,
        image_key: str,
        farmer_reported_symptoms: List[str]
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        doc = {
            "ownerUserId": ObjectId(owner_user_id),
            "farmId": ObjectId(farm_id),
            "cropType": crop_type.strip().lower(),
            "growthStage": growth_stage.strip().lower(),
            "status": "queued",
            "imageStorageKey": image_key,
            "farmerReportedSymptoms": farmer_reported_symptoms,
            "observations": [],
            "candidateExplanations": [],
            "weatherSnapshotId": None,
            "sourceReferences": [],
            "decision": None,
            "safetyReview": None,
            "failureCode": None,
            "createdAt": now,
            "updatedAt": now,
            "completedAt": None
        }
        res = await self.assessments.insert_one(doc)
        doc["_id"] = res.inserted_id
        return doc

    async def get_by_id(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(assessment_id)
        except Exception:
            return None
        return await self.assessments.find_one({"_id": oid})

    async def list_by_owner(
        self,
        owner_user_id: str,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[Dict[str, Any]], int]:
        try:
            oid = ObjectId(owner_user_id)
        except Exception:
            return [], 0
            
        skip = (page - 1) * page_size
        total = await self.assessments.count_documents({"ownerUserId": oid})
        cursor = self.assessments.find({"ownerUserId": oid}).sort("createdAt", -1).skip(skip).limit(page_size)
        items = await cursor.to_list(length=page_size)
        return items, total

    async def update_status(self, assessment_id: str, status: str, failure_code: Optional[str] = None):
        oid = ObjectId(assessment_id)
        update: Dict[str, Any] = {
            "status": status,
            "updatedAt": datetime.now(timezone.utc)
        }
        if failure_code:
            update["failureCode"] = failure_code
        await self.assessments.update_one({"_id": oid}, {"$set": update})

    async def save_results(
        self,
        assessment_id: str,
        observations: List[str],
        candidate_explanations: List[Dict[str, Any]],
        decision: Dict[str, Any],
        safety_review: Dict[str, Any],
        source_references: List[Dict[str, Any]],
        weather_snapshot_id: Optional[ObjectId] = None,
        status: str = "completed"
    ):
        oid = ObjectId(assessment_id)
        now = datetime.now(timezone.utc)
        update = {
            "status": status,
            "observations": observations,
            "candidateExplanations": candidate_explanations,
            "decision": decision,
            "safetyReview": safety_review,
            "sourceReferences": source_references,
            "weatherSnapshotId": weather_snapshot_id,
            "updatedAt": now,
            "completedAt": now if status == "completed" else None
        }
        await self.assessments.update_one({"_id": oid}, {"$set": update})

    async def add_followup(
        self,
        assessment_id: str,
        owner_user_id: str,
        question: str,
        answer: str,
        image_key: Optional[str] = None
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        doc = {
            "assessmentId": ObjectId(assessment_id),
            "ownerUserId": ObjectId(owner_user_id),
            "question": question,
            "answer": answer,
            "imageStorageKey": image_key,
            "createdAt": now
        }
        res = await self.followups.insert_one(doc)
        doc["_id"] = res.inserted_id
        return doc

    async def get_followups(self, assessment_id: str) -> List[Dict[str, Any]]:
        try:
            oid = ObjectId(assessment_id)
        except Exception:
            return []
        cursor = self.followups.find({"assessmentId": oid}).sort("createdAt", 1)
        return await cursor.to_list(length=20)

    async def delete_assessment(self, assessment_id: str, owner_user_id: str) -> bool:
        assessment = await self.get_by_id(assessment_id)
        if not assessment:
            raise NotFoundError("Assessment", assessment_id)
        if str(assessment["ownerUserId"]) != owner_user_id:
            raise AuthorizationError("You do not have permission to delete this assessment")

        await self.followups.delete_many({"assessmentId": ObjectId(assessment_id)})
        res = await self.assessments.delete_one({"_id": ObjectId(assessment_id)})
        return res.deleted_count > 0
