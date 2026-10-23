from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

class WeatherRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.weather_snapshots

    async def save_snapshot(self, farm_id: str, provider: str, normalized_data: Dict[str, Any], quality_metadata: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        doc = {
            "farmId": ObjectId(farm_id),
            "provider": provider,
            "dataType": "observation_and_forecast",
            "fetchedAt": now,
            "validTime": now + timedelta(hours=24),
            "normalizedData": normalized_data,
            "qualityMetadata": quality_metadata
        }
        res = await self.collection.insert_one(doc)
        doc["_id"] = res.inserted_id
        return doc

    async def get_latest_for_farm(self, farm_id: str, max_age_seconds: int = 3600) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(farm_id)
        except Exception:
            return None
        min_time = datetime.now(timezone.utc) - timedelta(seconds=max_age_seconds)
        return await self.collection.find_one(
            {"farmId": oid, "fetchedAt": {"$gte": min_time}},
            sort=[("fetchedAt", -1)]
        )
