"""
scripts/mongo_init.py — MongoDB Atlas Initializer & Index Creator for KrishiGuard AI
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, OperationFailure

# Load environment
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

def get_env_uri():
    env_file = ROOT_DIR / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("MONGODB_URI=") and not line.startswith("#"):
                    return line.split("=", 1)[1].strip()
    return os.environ.get("MONGODB_URI", "")

def init_database():
    uri = get_env_uri()
    if not uri:
        print("[ERROR] MONGODB_URI not found in .env or environment")
        sys.exit(1)

    db_name = os.environ.get("MONGODB_DATABASE", "krishiguard")
    print(f"Connecting to MongoDB Atlas cluster for database '{db_name}'...")

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=8000)
        # Ping
        client.admin.command('ping')
        print("[SUCCESS] MongoDB Atlas ping confirmed.")
        
        db = client[db_name]

        # 1. Users Indexes
        print("Ensuring indexes on 'users' collection...")
        db.users.create_index([("email", ASCENDING)], unique=True, name="uniq_users_email")
        db.users.create_index([("role", ASCENDING), ("isActive", ASCENDING)], name="idx_users_role_active")
        db.users.create_index([("createdAt", DESCENDING)], name="idx_users_created_at")

        # 2. Farms Indexes
        print("Ensuring indexes on 'farms' collection...")
        db.farms.create_index([("ownerUserId", ASCENDING), ("createdAt", DESCENDING)], name="idx_farms_owner_created")

        # 3. Assessments Indexes
        print("Ensuring indexes on 'assessments' collection...")
        db.assessments.create_index([("ownerUserId", ASCENDING), ("createdAt", DESCENDING)], name="idx_assessments_owner_created")
        db.assessments.create_index([("farmId", ASCENDING), ("createdAt", DESCENDING)], name="idx_assessments_farm_created")
        db.assessments.create_index([("status", ASCENDING), ("createdAt", ASCENDING)], name="idx_assessments_status_queue")

        # 4. Followups Indexes
        print("Ensuring indexes on 'followups' collection...")
        db.followups.create_index([("assessmentId", ASCENDING), ("createdAt", ASCENDING)], name="idx_followups_assessment_created")
        db.followups.create_index([("ownerUserId", ASCENDING)], name="idx_followups_owner")

        # 5. Weather Snapshots Indexes
        print("Ensuring indexes on 'weather_snapshots' collection...")
        db.weather_snapshots.create_index([("farmId", ASCENDING), ("fetchedAt", DESCENDING)], name="idx_weather_farm_fetched")

        # 6. Knowledge Sources Seed & Indexes
        print("Ensuring indexes on 'knowledge_sources' collection...")
        db.knowledge_sources.create_index([("diseaseKey", ASCENDING)], unique=True, name="uniq_knowledge_disease_key")
        db.knowledge_sources.create_index([("cropTypes", ASCENDING)], name="idx_knowledge_crop_types")

        # Seed Knowledge Base
        kb_path = ROOT_DIR / "knowledge_base" / "reviewed_sources.json"
        if kb_path.exists():
            with open(kb_path, "r", encoding="utf-8") as f:
                sources = json.load(f)
            
            inserted = 0
            updated = 0
            for item in sources:
                item["updatedAt"] = datetime.now(timezone.utc)
                if "reviewedAt" not in item:
                    item["reviewedAt"] = datetime.now(timezone.utc)
                res = db.knowledge_sources.update_one(
                    {"diseaseKey": item["diseaseKey"]},
                    {"$set": item},
                    upsert=True
                )
                if res.upserted_id:
                    inserted += 1
                elif res.modified_count > 0:
                    updated += 1
            print(f"[SUCCESS] Knowledge sources seeded. Upserted: {inserted}, Updated: {updated}, Total: {len(sources)}")

        print(f"[COMPLETE] Database '{db_name}' initialized successfully with all collections and indexes.")

    except ConnectionFailure as e:
        print(f"[ERROR] Failed to connect to MongoDB Atlas: {e}")
        sys.exit(1)
    except OperationFailure as e:
        print(f"[ERROR] MongoDB operation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()
