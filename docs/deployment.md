# KrishiGuard AI — Deployment Guide

## 1. Local Development (Docker Compose)

### Prerequisites:
- Docker 24+ & Docker Compose v2
- Node.js 20+ & Python 3.11+ (if running locally without containers)

### Quick Start:
1. Ensure `.env` is configured with your MongoDB Atlas connection string:
   ```bash
   cp .env.example .env
   # Edit MONGODB_URI and GEMINI_API_KEY
   ```

2. Initialize database indexes:
   ```bash
   python scripts/mongo_init.py
   ```

3. Spin up the entire multi-container stack:
   ```bash
   docker-compose up --build -d
   ```

4. Verify services:
   - Frontend: `http://localhost:3000`
   - FastAPI Docs: `http://localhost:8000/docs`
   - Healthcheck: `http://localhost:8000/api/v1/health/ready`
   - Redis: `localhost:6379`

---

## 2. Bare-Metal Local Development

### 1. Redis
Ensure Redis 7 is running:
```bash
docker run -d --name krishiguard-redis -p 6379:6379 redis:7-alpine
```

### 2. Backend API
```bash
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Background RQ Worker (Optional, handles async queue)
```bash
python -m backend.worker
```

### 4. Frontend Dev Server
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

---

## 3. Production Deployment (Google Cloud Run / Kubernetes)

### Frontend Hosting
- Deploy Nginx multi-stage build container to Cloud Run.
- Configure custom domain and SSL certificates.

### API & Worker
- Deploy FastAPI container to Cloud Run with minimum 1 instance to avoid cold starts.
- Set environment variables via Google Secret Manager:
  - `MONGODB_URI`
  - `GEMINI_API_KEY`
  - `SESSION_SECRET`
  - `CSRF_SECRET`
  - `REDIS_URL` (Google Cloud Memorystore for Redis or Upstash)
- Configure worker as a separate service or Cloud Run job.

### Healthcheck Endpoints
- Liveness: `/api/v1/health/live`
- Readiness: `/api/v1/health/ready`
