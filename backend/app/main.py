from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.core.errors import (
    KrishiGuardException,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitExceededError,
    ConflictError,
    ValidationError
)
from backend.app.database import DatabaseManager
from backend.app.redis_client import RedisManager
from backend.app.middleware.request_id import RequestIdMiddleware
from backend.app.middleware.security_headers import SecurityHeadersMiddleware
from backend.app.api.routes import auth, farms, assessments, health

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting KrishiGuard AI backend application...")
    await DatabaseManager.connect_db()
    await RedisManager.connect_redis()
    yield
    # Shutdown
    logger.info("Shutting down KrishiGuard AI backend...")
    await DatabaseManager.close_db()
    await RedisManager.close_redis()

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="Evidence-driven agricultural decision-support platform for farmers",
        lifespan=lifespan
    )

    # 1. Security & Traceability Middleware
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIdMiddleware)

    # 2. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS + ["https://ptw-1.onrender.com"],
        allow_origin_regex=r"https://.*\.onrender\.com|http://localhost:\d+|http://127\.0\.0\.1:\d+",
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "Retry-After", "X-CSRF-Token"]
    )

    # 3. Include Routers
    api_prefix = settings.API_V1_PREFIX
    app.include_router(health.router, prefix=api_prefix)
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(farms.router, prefix=api_prefix)
    app.include_router(assessments.router, prefix=api_prefix)

    # 4. Centralized Exception Handlers
    @app.exception_handler(KrishiGuardException)
    async def krishiguard_exception_handler(request: Request, exc: KrishiGuardException):
        req_id = getattr(request.state, "request_id", None)
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        headers = {}

        if isinstance(exc, AuthenticationError):
            status_code = status.HTTP_401_UNAUTHORIZED
        elif isinstance(exc, AuthorizationError):
            status_code = status.HTTP_403_FORBIDDEN
        elif isinstance(exc, NotFoundError):
            status_code = status.HTTP_404_NOT_FOUND
        elif isinstance(exc, ConflictError):
            status_code = status.HTTP_409_CONFLICT
        elif isinstance(exc, ValidationError):
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        elif isinstance(exc, RateLimitExceededError):
            status_code = status.HTTP_429_TOO_MANY_REQUESTS
            headers["Retry-After"] = str(exc.retry_after)

        return JSONResponse(
            status_code=status_code,
            headers=headers,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details
                },
                "request_id": req_id
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        req_id = getattr(request.state, "request_id", None)
        errors = []
        for err in exc.errors():
            loc = " -> ".join(str(l) for l in err.get("loc", []))
            errors.append({"field": loc, "message": err.get("msg")})

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "REQUEST_VALIDATION_ERROR",
                    "message": "Invalid request parameters or payload",
                    "details": errors
                },
                "request_id": req_id
            }
        )

    @app.exception_handler(Exception)
    async def global_unhandled_exception_handler(request: Request, exc: Exception):
        req_id = getattr(request.state, "request_id", None)
        logger.error(f"Unhandled server error [req_id={req_id}]: {exc}", exc_info=True)
        # Never leak stack traces, database strings, or internal errors to client
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred while processing your request. Please contact support."
                },
                "request_id": req_id
            }
        )

    return app

app = create_application()
