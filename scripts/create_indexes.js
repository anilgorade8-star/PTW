// scripts/create_indexes.js
// Run with: mongosh "$MONGODB_URI" scripts/create_indexes.js

const dbName = process.env.MONGODB_DATABASE || 'krishiguard';
const db = db.getSiblingDB(dbName);

print(`Creating indexes and collection validation for database: ${dbName}`);

// 1. Users collection
db.users.createIndex({ email: 1 }, { unique: true, name: "uniq_users_email" });
db.users.createIndex({ role: 1, isActive: 1 }, { name: "idx_users_role_active" });
db.users.createIndex({ createdAt: -1 }, { name: "idx_users_created_at" });

// 2. Farms collection
db.farms.createIndex({ ownerUserId: 1, createdAt: -1 }, { name: "idx_farms_owner_created" });
db.farms.createIndex({ "location.coordinates": "2dsphere" }, { sparse: true, name: "idx_farms_geo_2dsphere" });

// 3. Assessments collection
db.assessments.createIndex({ ownerUserId: 1, createdAt: -1 }, { name: "idx_assessments_owner_created" });
db.assessments.createIndex({ farmId: 1, createdAt: -1 }, { name: "idx_assessments_farm_created" });
db.assessments.createIndex({ status: 1, createdAt: 1 }, { name: "idx_assessments_status_queue" });
db.assessments.createIndex({ imageStorageKey: 1 }, { name: "idx_assessments_image_key" });

// 4. Followups collection
db.followups.createIndex({ assessmentId: 1, createdAt: 1 }, { name: "idx_followups_assessment_created" });
db.followups.createIndex({ ownerUserId: 1 }, { name: "idx_followups_owner" });

// 5. Weather snapshots collection
db.weather_snapshots.createIndex({ farmId: 1, fetchedAt: -1 }, { name: "idx_weather_farm_fetched" });
db.weather_snapshots.createIndex({ validTime: 1 }, { expireAfterSeconds: 86400, name: "ttl_weather_valid_time" });

// 6. Knowledge sources collection
db.knowledge_sources.createIndex({ diseaseKey: 1 }, { unique: true, name: "uniq_knowledge_disease_key" });
db.knowledge_sources.createIndex({ cropTypes: 1 }, { name: "idx_knowledge_crop_types" });

print("Indexes successfully created.");
