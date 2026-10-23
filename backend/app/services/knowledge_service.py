from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.app.repositories.knowledge_repo import KnowledgeRepository
from backend.app.core.logging import logger
import json
from pathlib import Path

class KnowledgeService:
    @classmethod
    async def get_all_sources(cls, db: Optional[AsyncIOMotorDatabase] = None) -> List[Dict[str, Any]]:
        if db is not None:
            try:
                repo = KnowledgeRepository(db)
                sources = await repo.get_all_sources("tomato")
                if sources:
                    return sources
            except Exception as e:
                logger.warning(f"Error querying knowledge sources from MongoDB: {e}")

        # Fallback to local reviewed_sources.json
        candidate_paths = [
            Path(__file__).resolve().parent.parent.parent / "knowledge_base" / "reviewed_sources.json",
            Path(__file__).resolve().parent.parent.parent.parent / "knowledge_base" / "reviewed_sources.json",
            Path("/app/backend/knowledge_base/reviewed_sources.json"),
            Path("/app/knowledge_base/reviewed_sources.json"),
        ]
        for kb_path in candidate_paths:
            if kb_path.exists():
                with open(kb_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        return []

    @classmethod
    async def get_source_for_disease(cls, disease_key: str, db: Optional[AsyncIOMotorDatabase] = None) -> Optional[Dict[str, Any]]:
        sources = await cls.get_all_sources(db)
        for s in sources:
            if s.get("diseaseKey") == disease_key:
                return s
        return None
