from datetime import datetime, timezone
from typing import Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.app.core.errors import ConflictError

class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.users

    async def create_user(self, name: str, email: str, password_hash: str, role: str = "farmer") -> Dict[str, Any]:
        normalized_email = email.strip().lower()
        now = datetime.now(timezone.utc)
        
        # Check if already exists
        existing = await self.collection.find_one({"email": normalized_email})
        if existing:
            raise ConflictError("An account with this email address already exists")

        user_doc = {
            "name": name.strip(),
            "email": normalized_email,
            "passwordHash": password_hash,
            "role": role,
            "isActive": True,
            "createdAt": now,
            "updatedAt": now
        }
        res = await self.collection.insert_one(user_doc)
        user_doc["_id"] = res.inserted_id
        return user_doc

    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"email": email.strip().lower()})

    async def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(user_id)
        except Exception:
            return None
        return await self.collection.find_one({"_id": oid})

    async def update_password(self, user_id: str, new_password_hash: str) -> bool:
        try:
            oid = ObjectId(user_id)
        except Exception:
            return False
        res = await self.collection.update_one(
            {"_id": oid},
            {"$set": {"passwordHash": new_password_hash, "updatedAt": datetime.now(timezone.utc)}}
        )
        return res.modified_count > 0

    async def update_profile(self, user_id: str, update_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(user_id)
        except Exception:
            return None
        update_dict["updatedAt"] = datetime.now(timezone.utc)
        await self.collection.update_one({"_id": oid}, {"$set": update_dict})
        return await self.get_by_id(user_id)
