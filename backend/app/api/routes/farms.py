from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.app.database import get_db
from backend.app.repositories.farm_repo import FarmRepository
from backend.app.schemas.farm import FarmCreateRequest, FarmUpdateRequest, FarmResponse
from backend.app.schemas.common import ApiResponse
from backend.app.api.dependencies.auth import get_current_user, verify_csrf
from backend.app.core.errors import NotFoundError, AuthorizationError

router = APIRouter(prefix="/farms", tags=["Farms"])

def _format_farm(doc: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(doc["_id"]),
        "ownerUserId": str(doc["ownerUserId"]),
        "name": doc["name"],
        "location": doc["location"],
        "cropTypes": doc.get("cropTypes", ["tomato"]),
        "sizeInAcres": doc.get("sizeInAcres"),
        "createdAt": doc["createdAt"],
        "updatedAt": doc["updatedAt"]
    }

@router.post("", response_model=ApiResponse[FarmResponse], status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_csrf)])
async def create_farm(
    req: FarmCreateRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    repo = FarmRepository(db)
    user_id = str(user["_id"])
    doc = await repo.create_farm(
        owner_user_id=user_id,
        farm_data=req.model_dump()
    )
    return ApiResponse(data=_format_farm(doc))

@router.get("", response_model=ApiResponse[List[FarmResponse]])
async def list_farms(
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    repo = FarmRepository(db)
    user_id = str(user["_id"])
    farms = await repo.list_by_owner(user_id)
    return ApiResponse(data=[_format_farm(f) for f in farms])

@router.get("/{farm_id}", response_model=ApiResponse[FarmResponse])
async def get_farm(
    farm_id: str,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    repo = FarmRepository(db)
    farm = await repo.get_by_id(farm_id)
    if not farm:
        raise NotFoundError("Farm", farm_id)
    if str(farm["ownerUserId"]) != str(user["_id"]):
        raise AuthorizationError("You do not have permission to view this farm.")
    return ApiResponse(data=_format_farm(farm))

@router.patch("/{farm_id}", response_model=ApiResponse[FarmResponse], dependencies=[Depends(verify_csrf)])
async def update_farm(
    farm_id: str,
    req: FarmUpdateRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    repo = FarmRepository(db)
    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    farm = await repo.update_farm(farm_id, str(user["_id"]), update_data)
    return ApiResponse(data=_format_farm(farm))

@router.delete("/{farm_id}", response_model=ApiResponse[bool], dependencies=[Depends(verify_csrf)])
async def delete_farm(
    farm_id: str,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    repo = FarmRepository(db)
    success = await repo.delete_farm(farm_id, str(user["_id"]))
    return ApiResponse(data=success)
