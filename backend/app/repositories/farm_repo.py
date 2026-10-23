from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.app.core.errors import NotFoundError, AuthorizationError

class FarmRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.farms

    async def create_farm(self, owner_user_id: str, farm_data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        doc = {
            "ownerUserId": ObjectId(owner_user_id),
            "name": farm_data["name"].strip(),
            "location": farm_data["location"],
            "cropTypes": farm_data.get("cropTypes", ["tomato"]),
            "sizeInAcres": farm_data.get("sizeInAcres"),
            "createdAt": now,
            "updatedAt": now
        }
        res = await self.collection.insert_one(doc)
        doc["_id"] = res.inserted_id
        return doc

    async def get_by_id(self, farm_id: str) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(farm_id)
        except Exception:
            return None
        return await self.collection.find_one({"_id": oid})

    async def list_by_owner(self, owner_user_id: str) -> List[Dict[str, Any]]:
        try:
            oid = ObjectId(owner_user_id)
        except Exception:
            return []
        cursor = self.collection.find({"ownerUserId": oid}).sort("createdAt", -1)
        return await cursor.to_list(length=100)

    async def update_farm(self, farm_id: str, owner_user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        farm = await self.get_by_id(farm_id)
        if not farm:
            raise NotFoundError("Farm", farm_id)
        if str(farm["ownerUserId"]) != owner_user_id:
            raise AuthorizationError("You do not have permission to modify this farm")

        update_data["updatedAt"] = datetime.now(timezone.utc)
        await self.collection.update_one({"_id": ObjectId(farm_id)}, {"$set": update_data})
        return await self.get_by_id(farm_id)

    async def delete_farm(self, farm_id: str, owner_user_id: str) -> bool:
        farm = await self.get_by_id(farm_id)
        if not farm:
            raise NotFoundError("Farm", farm_id)
        if str(farm["ownerUserId"]) != owner_user_id:
            raise AuthorizationError("You do not have permission to delete this farm")

        res = await self.collection.delete_one({"_id": ObjectId(farm_id)})
        return res.deleted_count > 0
