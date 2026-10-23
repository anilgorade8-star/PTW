from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

class KnowledgeRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.knowledge_sources

    async def get_all_sources(self, crop_type: str = "tomato") -> List[Dict[str, Any]]:
        cursor = self.collection.find({"cropTypes": crop_type})
        return await cursor.to_list(length=50)

    async def get_by_disease_key(self, disease_key: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"diseaseKey": disease_key})
