# KrishiGuard AI — API Specification

Base URL: `/api/v1`

## 1. Authentication Endpoints

### Register
- **URL:** `POST /api/v1/auth/register`
- **Rate Limit:** 10 / 10 min
- **Request:**
  ```json
  {
    "name": "Ramesh Patil",
    "email": "ramesh@example.com",
    "password": "StrongPassword123",
    "confirm_password": "StrongPassword123"
  }
  ```
- **Response:** `200 OK` (Sets HttpOnly `kg_session_id` cookie)
  ```json
  {
    "success": true,
    "data": {
      "user": { "id": "...", "name": "...", "email": "...", "role": "farmer" },
      "csrfToken": "..."
    }
  }
  ```

### Login
- **URL:** `POST /api/v1/auth/login`
- **Rate Limit:** 5 / 15 min
- **Request:**
  ```json
  { "email": "ramesh@example.com", "password": "StrongPassword123" }
  ```
- **Response:** `200 OK` (Sets HttpOnly `kg_session_id` cookie)

### Logout
- **URL:** `POST /api/v1/auth/logout`
- **Response:** `200 OK` (Clears session cookie and deletes from Redis)

### Current User
- **URL:** `GET /api/v1/auth/me`
- **Response:** `200 OK` returns authenticated user profile & fresh CSRF token.

---

## 2. Farm Management

### Create Farm
- **URL:** `POST /api/v1/farms`
- **Headers:** `X-CSRF-Token`
- **Request:**
  ```json
  {
    "name": "North Field Block",
    "location": {
      "latitude": 19.9975,
      "longitude": 73.7898,
      "district": "Nashik",
      "state": "Maharashtra"
    },
    "cropTypes": ["tomato"],
    "sizeInAcres": 2.5
  }
  ```
- **Response:** `201 Created`

### List Farms
- **URL:** `GET /api/v1/farms`
- **Response:** `200 OK` returns array of farms belonging to the authenticated user.

### Delete Farm
- **URL:** `DELETE /api/v1/farms/{farm_id}`
- **Headers:** `X-CSRF-Token`
- **Response:** `200 OK`

---

## 3. Assessments & Diagnostic Pipeline

### Submit Assessment
- **URL:** `POST /api/v1/assessments`
- **Rate Limit:** 20 / hour
- **Content-Type:** `multipart/form-data`
- **Form Fields:**
  - `image`: Binary file (JPEG, PNG, WebP)
  - `farmId`: string (ID of user's farm)
  - `cropType`: string ("tomato")
  - `growthStage`: string ("seedling" | "vegetative" | "flowering" | "fruiting" | "harvest")
  - `symptoms`: stringified JSON or comma-separated symptoms
- **Response:** `202 Accepted`

### Get Assessment Details
- **URL:** `GET /api/v1/assessments/{assessment_id}`
- **Response:** `200 OK`
  Returns assessment record, status (`queued` | `processing` | `awaiting_farmer_input` | `completed` | `failed`), observations, candidate explanations, weather snapshot, farmer action plan, and safety review.

### Submit Follow-up Answer
- **URL:** `POST /api/v1/assessments/{assessment_id}/followups`
- **Headers:** `X-CSRF-Token`
- **Request:**
  ```json
  { "answer": "The spots started strictly on the lower oldest leaves near the soil." }
  ```
- **Response:** `200 OK` (Re-runs pipeline with new evidence)

---

## 4. Health & Monitoring

### Liveness Probe
- **URL:** `GET /api/v1/health/live`
- **Response:** `{"status": "alive"}`

### Readiness Probe
- **URL:** `GET /api/v1/health/ready`
- **Response:** `200 OK`
  ```json
  {
    "status": "ready",
    "services": {
      "database": "connected",
      "cache_queue": "connected"
    }
  }
  ```
