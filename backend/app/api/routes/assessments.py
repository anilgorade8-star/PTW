import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, Header, Response, status
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.app.core.config import settings
from backend.app.database import get_db
from backend.app.repositories.assessment_repo import AssessmentRepository
from backend.app.repositories.farm_repo import FarmRepository
from backend.app.repositories.weather_repo import WeatherRepository
from backend.app.services.assessment_service import AssessmentService
from backend.app.services.storage_service import storage_service
from backend.app.schemas.assessment import (
    AssessmentResponse,
    AssessmentListItem,
    FollowupSubmitRequest
)
from backend.app.schemas.common import ApiResponse, PaginatedResponse
from backend.app.api.dependencies.auth import get_current_user, verify_csrf
from backend.app.api.dependencies.rate_limit import rate_limit
from backend.app.core.errors import NotFoundError, AuthorizationError, ValidationError

router = APIRouter(prefix="/assessments", tags=["Assessments"])

async def _build_assessment_response(doc: Dict[str, Any], db: AsyncIOMotorDatabase) -> Dict[str, Any]:
    assessment_repo = AssessmentRepository(db)
    weather_repo = WeatherRepository(db)

    followups = await assessment_repo.get_followups(str(doc["_id"]))
    weather_snap = None
    if doc.get("weatherSnapshotId"):
        snap_doc = await db.weather_snapshots.find_one({"_id": doc["weatherSnapshotId"]})
        if snap_doc:
            weather_snap = {
                "id": str(snap_doc["_id"]),
                "farmId": str(snap_doc["farmId"]),
                "provider": snap_doc.get("provider", "open-meteo"),
                "fetchedAt": snap_doc["fetchedAt"],
                "validTime": snap_doc["validTime"],
                "normalizedData": snap_doc["normalizedData"],
                "qualityMetadata": snap_doc.get("qualityMetadata", {})
            }

    formatted_followups = [
        {
            "id": str(f["_id"]),
            "question": f["question"],
            "answer": f["answer"],
            "imageStorageKey": f.get("imageStorageKey"),
            "createdAt": f["createdAt"]
        }
        for f in followups
    ]

    return {
        "id": str(doc["_id"]),
        "ownerUserId": str(doc["ownerUserId"]),
        "farmId": str(doc["farmId"]),
        "cropType": doc.get("cropType", "tomato"),
        "growthStage": doc.get("growthStage", "vegetative"),
        "status": doc.get("status", "queued"),
        "imageStorageKey": doc.get("imageStorageKey", ""),
        "imageUrl": f"/api/v1/assessments/images/{doc.get('imageStorageKey', '')}",
        "farmerReportedSymptoms": doc.get("farmerReportedSymptoms", []),
        "observations": doc.get("observations", []),
        "candidateExplanations": doc.get("candidateExplanations", []),
        "weatherSnapshot": weather_snap,
        "sourceReferences": doc.get("sourceReferences", []),
        "decision": doc.get("decision"),
        "safetyReview": doc.get("safetyReview"),
        "followups": formatted_followups,
        "failureCode": doc.get("failureCode"),
        "createdAt": doc["createdAt"],
        "updatedAt": doc["updatedAt"],
        "completedAt": doc.get("completedAt")
    }

@router.post(
    "",
    response_model=ApiResponse[Dict[str, Any]],
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(rate_limit("create_assessment", settings.RATE_LIMIT_ASSESSMENT_MAX, settings.RATE_LIMIT_ASSESSMENT_WINDOW_SECONDS))]
)
async def create_assessment(
    image: UploadFile = File(..., description="Crop photograph (JPEG, PNG, WebP)"),
    farmId: str = Form(...),
    cropType: str = Form("tomato"),
    growthStage: str = Form("vegetative"),
    symptoms: Optional[str] = Form(None, description="Comma-separated or JSON list of symptoms"),
    idempotencyKey: Optional[str] = Header(None, alias="X-Idempotency-Key"),
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    # Parse symptoms
    parsed_symptoms: List[str] = []
    if symptoms:
        try:
            val = json.loads(symptoms)
            if isinstance(val, list):
                parsed_symptoms = [str(x).strip() for x in val if str(x).strip()]
            else:
                parsed_symptoms = [s.strip() for s in symptoms.split(",") if s.strip()]
        except Exception:
            parsed_symptoms = [s.strip() for s in symptoms.split(",") if s.strip()]

    file_bytes = await image.read()
    if not file_bytes:
        raise ValidationError("Uploaded image file is empty.")

    assessment_doc = await AssessmentService.create_assessment(
        db=db,
        owner_user_id=str(user["_id"]),
        farm_id=farmId,
        crop_type=cropType,
        growth_stage=growthStage,
        image_bytes=file_bytes,
        filename=image.filename or "crop.jpg",
        reported_symptoms=parsed_symptoms,
        idempotency_key=idempotencyKey
    )

    resp_data = await _build_assessment_response(assessment_doc, db)
    return ApiResponse(data=resp_data)

@router.get("", response_model=ApiResponse[PaginatedResponse[AssessmentListItem]])
async def list_assessments(
    page: int = 1,
    page_size: int = 10,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    repo = AssessmentRepository(db)
    farm_repo = FarmRepository(db)
    user_id = str(user["_id"])
    
    items, total = await repo.list_by_owner(user_id, page=page, page_size=page_size)

    # Fetch farm names for convenience
    farms = await farm_repo.list_by_owner(user_id)
    farm_name_map = {str(f["_id"]): f["name"] for f in farms}

    formatted_items: List[AssessmentListItem] = []
    for doc in items:
        f_id = str(doc.get("farmId", ""))
        primary_cond = None
        certainty = None
        if doc.get("decision"):
            primary_cond = doc["decision"].get("primaryCondition")
            certainty = doc["decision"].get("certaintyLevel")

        formatted_items.append(
            AssessmentListItem(
                id=str(doc["_id"]),
                farmId=f_id,
                farmName=farm_name_map.get(f_id, "Farm"),
                cropType=doc.get("cropType", "tomato"),
                growthStage=doc.get("growthStage", "vegetative"),
                status=doc.get("status", "queued"),
                primaryCondition=primary_cond,
                certaintyLevel=certainty,
                imageUrl=f"/api/v1/assessments/images/{doc.get('imageStorageKey', '')}",
                createdAt=doc["createdAt"],
                completedAt=doc.get("completedAt")
            )
        )

    return ApiResponse(
        data=PaginatedResponse(
            items=formatted_items,
            total=total,
            page=page,
            page_size=page_size,
            has_more=(page * page_size) < total
        )
    )

@router.get("/{assessment_id}", response_model=ApiResponse[Dict[str, Any]])
async def get_assessment(
    assessment_id: str,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    repo = AssessmentRepository(db)
    doc = await repo.get_by_id(assessment_id)
    if not doc:
        raise NotFoundError("Assessment", assessment_id)
    if str(doc["ownerUserId"]) != str(user["_id"]):
        raise AuthorizationError("You do not have permission to view this assessment.")

    data = await _build_assessment_response(doc, db)
    return ApiResponse(data=data)

@router.post("/{assessment_id}/followups", response_model=ApiResponse[Dict[str, Any]], dependencies=[Depends(verify_csrf)])
async def submit_followup(
    assessment_id: str,
    req: FollowupSubmitRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    repo = AssessmentRepository(db)
    doc = await repo.get_by_id(assessment_id)
    if not doc:
        raise NotFoundError("Assessment", assessment_id)
    if str(doc["ownerUserId"]) != str(user["_id"]):
        raise AuthorizationError("You do not have permission to update this assessment.")

    # Record the followup
    question = "Additional diagnostic inquiry"
    if doc.get("decision") and doc["decision"].get("suggestedFollowupQuestion"):
        question = doc["decision"]["suggestedFollowupQuestion"]

    await repo.add_followup(
        assessment_id=assessment_id,
        owner_user_id=str(user["_id"]),
        question=question,
        answer=req.answer
    )

    # Re-evaluate with additional farmer context
    combined_symptoms = doc.get("farmerReportedSymptoms", []) + [req.answer]
    await db.assessments.update_one(
        {"_id": doc["_id"]},
        {"$set": {"farmerReportedSymptoms": combined_symptoms}}
    )

    # Rerun pipeline
    await AssessmentService.run_pipeline(assessment_id, db)

    updated_doc = await repo.get_by_id(assessment_id)
    resp_data = await _build_assessment_response(updated_doc, db)
    return ApiResponse(data=resp_data)

@router.get("/images/{storage_key}")
async def get_assessment_image(
    storage_key: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Authorized image retrieval. Prevents unauthorized public access to farmer crop photos.
    """
    path = storage_service.get_image_path(storage_key)
    if not path or not path.exists():
        raise NotFoundError("Image", storage_key)

    ext = path.suffix.lower()
    media_type = "image/jpeg" if ext in [".jpg", ".jpeg"] else ("image/png" if ext == ".png" else "image/webp")
    return FileResponse(path=path, media_type=media_type, headers={"Cache-Control": "private, max-age=86400"})

@router.delete("/{assessment_id}", response_model=ApiResponse[bool], dependencies=[Depends(verify_csrf)])
async def delete_assessment(
    assessment_id: str,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    repo = AssessmentRepository(db)
    success = await repo.delete_assessment(assessment_id, str(user["_id"]))
    return ApiResponse(data=success)
