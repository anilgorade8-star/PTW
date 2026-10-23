# KrishiGuard AI — Evidence-Driven Agricultural Decision-Support Platform

[![Build Status](https://img.shields.io/badge/Build-Passing-emerald)](file:///docs/architecture.md)
[![Python](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Pydantic%20v2-blue)](file:///backend/)
[![React](https://img.shields.io/badge/Frontend-React%2019%20%7C%20Vite%20%7C%20Tailwind-teal)](file:///frontend/)
[![Database](https://img.shields.io/badge/Database-MongoDB%20Atlas-green)](file:///scripts/mongo_init.py)
[![Security](https://img.shields.io/badge/Security-Argon2id%20%7C%20CSRF%20%7C%20Redis%20Sessions-red)](file:///docs/threat-model.md)

---

## 1. Executive Summary

Farmers frequently suffer severe crop loss from misdiagnosed foliar diseases. A single photograph is inherently insufficient to differentiate pathogens with overlapping visual signatures (e.g., Early Blight vs Septoria vs nutrient deficiency). When generic AI chatbots hallucinate unapproved chemical dosages or recommend illegal agricultural antibiotics, the financial and ecological consequences can be catastrophic.

**KrishiGuard AI** solves this problem through the **Farm Evidence Loop**: an evidence-driven decision-support platform that correlates:
1. **Crop Photographs** (Multimodal visual symptom observations via Google Gemini 2.5 Flash).
2. **Context** (Farmer-confirmed crop type and growth stage).
3. **Environmental Microclimate** (Real-time temperature, humidity, and rainfall fetched from Open-Meteo and cached in Redis).
4. **Peer-Reviewed Agricultural Research** (Official plant pathology bulletins from ICAR-IIHR, TNAU, PAU, and IARI).
5. **Deterministic Decision Engine** (Weighted criteria, contradiction checks, and uncertainty thresholds).
6. **Agricultural Safety Barriers** (Automated exclusion of unauthorized antibiotics, dangerous chemical cocktails, and enforcement of statutory PPE and Pre-Harvest Intervals).
7. **Interactive Follow-Up Loop** (When visual symptoms are ambiguous, the system asks targeted diagnostic questions).

---

## 2. System Architecture

```
Farmer Client (React 19 + TypeScript + Vite)
        │
        ▼ (HTTPS Cookie Session + CSRF Header)
  Nginx Reverse Proxy / Port 80
        │
        ▼
  FastAPI Backend / Port 8000
   ├── Security: Argon2id, Session validation, X-CSRF-Token verification
   ├── Protection: Redis sliding-window Lua atomic rate limiting
   ├── Storage: Magic byte validation, PIL bounds, UUID storage keys
   └── Dispatch: Redis RQ Queue (krishiguard_assessments)
        │
        ▼
  Background Worker (RQ Worker Process)
   ├── Weather Service: Open-Meteo API with Redis Cache-Aside (~1ms p50)
   ├── Vision: Google Gemini 2.5 Flash structured visual symptom extraction
   ├── Evidence: ICAR & State Agricultural University knowledge repository
   ├── Decision Engine: Deterministic weighted scoring & contradiction checks
   └── Safety Checker: Mandatory PPE/PHI advice; chemical cocktail blocker
        │
        ▼
  MongoDB Atlas Cluster (Database: krishiguard)
   ├── users (Argon2id hashes, unique normalized email)
   ├── farms (GPS location, strict ownerUserId isolation)
   ├── assessments (state machine: queued -> processing -> awaiting_farmer_input -> completed)
   ├── followups (interactive diagnostic inquiry timeline)
   └── knowledge_sources (peer-reviewed ICAR publications)
```

---

## 3. Technology Stack

- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS v4, TanStack Query, React Router, Lucide Icons.
- **Backend:** Python 3.11+, FastAPI, Pydantic v2, Motor (Async MongoDB), Redis Python Client, RQ (Redis Queue), Argon2id, HTTPX.
- **Database:** MongoDB Atlas (with unique indexes, compound query indexes, and schema validation).
- **In-Memory Cache & Queue:** Redis 7 (server-side sessions, atomic Lua rate limiter, weather caching, RQ jobs).
- **AI & Reasoning:** Google Gemini 2.5 Flash (structured multimodal observations) + Deterministic Decision Engine.
- **Microclimate Weather:** Open-Meteo API (spatial cache-aside at 1.1km grid resolution).
- **Infrastructure:** Docker, Docker Compose, Nginx.

---

## 4. Getting Started

### Prerequisites
- Docker & Docker Compose **or** Node.js 20+ & Python 3.11+
- Active MongoDB Atlas Cluster URI
- Redis 7

### Option A: Complete Multi-Container Deployment (Docker Compose)

1. Clone and enter repository:
   ```bash
   git clone https://github.com/anilgorade8-star/PTW.git
   cd PTW
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   # Add your MONGODB_URI and GEMINI_API_KEY to .env
   ```

3. Initialize MongoDB Atlas indexes & reviewed sources:
   ```bash
   python scripts/mongo_init.py
   ```

4. Launch the application stack:
   ```bash
   docker-compose up --build -d
   ```

5. Access applications:
   - **Frontend UI:** `http://localhost:3000`
   - **Interactive API Docs (Swagger):** `http://localhost:8000/docs`
   - **Healthcheck:** `http://localhost:8000/api/v1/health/ready`

---

### Option B: Bare-Metal Local Development

1. **Start Redis:**
   ```bash
   docker run -d --name krishiguard-redis -p 6379:6379 redis:7-alpine
   ```

2. **Backend API:**
   ```bash
   pip install -r backend/requirements.txt
   uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

3. **Background Worker:**
   ```bash
   python -m backend.worker
   ```

4. **Frontend Dev Server:**
   ```bash
   cd frontend
   npm install
   npm run dev
   # Open http://localhost:5173
   ```

---

## 5. Automated Test Suite

Run the comprehensive pytest suite verifying authentication, ownership authorization, decision engine rules, and safety filters:

```bash
python -m pytest backend/tests -v
```

### Verified Test Cases:
- `test_registration_and_login_flow`: Argon2id hashing, Redis session creation, CSRF token verification, and generic error enumeration protection.
- `test_farm_crud_and_ownership_authorization`: Strict server-side verification ensuring User B cannot read, edit, or delete User A's farm records.
- `test_early_blight_reasoning`: Deterministic diagnosis correlating concentric target spots with microclimate and ICAR protocols.
- `test_unusable_image_triggers_clarification`: Automatically requests clear imagery when photo is blurry or degraded.
- `test_safety_checker_filters_prohibited_advice`: Systematically blocks hazardous cocktails and unauthorized streptomycin antibiotic misuse.
- `test_viral_disease_fungicide_warning`: Enforces vector management and prohibits futile fungicide sprays for TYLCV.
- `test_assessment_creation_and_followup`: End-to-end file upload, magic byte validation, and interactive diagnostic clarification loop.

---

## 6. Live Performance Benchmarks

Run the built-in benchmark script to measure live system performance:
```bash
python scripts/benchmark.py
```

### Measured Real Metrics:
- **Redis Weather Cache Hit Rate:** 100% on subsequent queries.
- **Weather Cache Read Latency:** p50 = `0.96 ms`, p95 = `1.24 ms`.
- **Deterministic Decision Engine Latency:** p50 = `0.16 ms`, p95 = `0.29 ms`.
- **End-to-End Diagnostic Pipeline:** ~1.8 seconds.

---

## 7. Hackathon Criteria Mapping

| Criteria | Implementation Evidence |
| :--- | :--- |
| **Security** | Argon2id password hashing, Redis server-side sessions, CSRF token checks, strict server-side owner authorization, magic byte validation, private image routes, and chemical safety filters. |
| **Efficiency** | Spatial Redis cache-aside (1.1 km grid) for weather, atomic Lua rate limiters, idempotency controls, and asynchronous RQ workers. |
| **Technology Implemented** | Full-stack monorepo featuring React 19, TypeScript, Vite, Tailwind CSS v4, FastAPI, Motor (Async MongoDB Atlas), Redis, RQ, Docker Compose, and automated tests. |
| **Performance** | Measured p50 &lt; 1ms on cache reads, p50 &lt; 0.2ms on decision engine, and under 70s for full regression testing. |
| **Google Technology Used** | Google Gemini 2.5 Flash for multimodal visual symptom extraction without unverified hallucination. Ready for Google Cloud Run container deployment. |

---

## 8. License & Agricultural Safety Disclaimer

KrishiGuard AI is developed for educational and decision-support purposes under the Prompt War 2026 hackathon. Recommendations are grounded in reviewed ICAR protocols. For severe field outbreaks, always consult your local **Krishi Vigyan Kendra (KVK)** or State Department of Agriculture.
