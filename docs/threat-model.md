# KrishiGuard AI — Threat Model & Security Architecture

## 1. Threat Landscape & Mitigations

### 1.1 Credential & Session Security
- **Threat:** Brute-force dictionary attacks, rainbow table lookups, credential stuffing.
- **Mitigation:**
  - Passwords hashed using **Argon2id** (`time_cost=2`, `memory_cost=65536` [64MB RAM], `parallelism=1`).
  - Session tokens generated via cryptographic PRNG (`secrets.token_urlsafe(32)`).
  - Raw session IDs are stored only in client HttpOnly cookies; Redis stores the SHA-256 hash under `kg:session:v1:{hash}`.
  - Generic error messages ("Invalid email or password") prevent account enumeration.

### 1.2 Cross-Site Request Forgery (CSRF)
- **Threat:** Third-party websites issuing state-changing requests using ambient cookies.
- **Mitigation:**
  - `SameSite=Lax` / `Strict` cookie configuration.
  - Synchronizer HMAC-SHA256 tokens (`X-CSRF-Token`) generated per session and validated on all state-changing endpoints (`POST`, `PUT`, `PATCH`, `DELETE`).

### 1.3 Insecure Direct Object References (IDOR)
- **Threat:** User A tampering with or reading User B's farm, crop photographs, or assessments.
- **Mitigation:**
  - Strict server-side ownership authorization on every query. Every farm and assessment lookup queries by both `_id` and `ownerUserId`.
  - Image files are served via `/api/v1/assessments/images/{storage_key}` requiring active session verification.

### 1.4 Malicious File Upload & Directory Traversal
- **Threat:** Upload of PHP/executable scripts masked as images, image zip bombs, or `../` path traversal.
- **Mitigation:**
  - File signature inspection (magic bytes: `\xff\xd8\xff` for JPEG, `\x89PNG` for PNG, `RIFF...WEBP` for WebP).
  - PIL decoding verification and image dimension enforcement (min 50x50px, max 4096x4096px).
  - Size ceiling enforced at 5 MB.
  - Storage key generated as clean hex UUID (`uuid4().hex.jpg`); directory traversal input is stripped via `Path(key).name`.

### 1.5 Rate Limiting & Denial of Service
- **Threat:** Flooding login endpoints or triggering expensive AI jobs repeatedly.
- **Mitigation:**
  - Atomic Redis sliding window Lua scripts (`ZREMRANGEBYSCORE`, `ZCARD`, `ZADD`, `EXPIRE`).
  - Distinct limits:
    - Login: 5 attempts per 15 minutes.
    - Registration: 10 requests per 10 minutes.
    - Assessment creation: 20 assessments per hour.
    - General API: 120 requests per minute.
  - Return HTTP 429 with explicit `Retry-After` header.

### 1.6 AI Prompt Injection & Toxic Advice
- **Threat:** Hallucinated chemical cocktail recommendations or user prompt injection.
- **Mitigation:**
  - Gemini model output is strictly bounded to structured Pydantic schemas.
  - Gemini outputs visual observations only; final diagnosis is calculated by the deterministic `DecisionEngine`.
  - `SafetyChecker` systematically scans and blocks unapproved antibiotic sprays (streptomycin misuse), unverified chemical cocktails, and enforces mandatory PPE & Pre-Harvest Intervals.
