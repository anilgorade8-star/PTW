from typing import Dict, Any
from fastapi import APIRouter, Depends, Response, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.app.core.config import settings
from backend.app.core.security import (
    hash_password,
    verify_password,
    generate_csrf_token
)
from backend.app.core.errors import AuthenticationError, ValidationError
from backend.app.database import get_db
from backend.app.repositories.user_repo import UserRepository
from backend.app.services.session_service import SessionService
from backend.app.schemas.user import (
    RegisterRequest,
    LoginRequest,
    UserProfileResponse,
    PasswordChangeRequest,
    PasswordResetRequest,
    PasswordResetConfirmRequest
)
from backend.app.schemas.common import ApiResponse
from backend.app.api.dependencies.auth import get_current_user, verify_csrf
from backend.app.api.dependencies.rate_limit import rate_limit

router = APIRouter(prefix="/auth", tags=["Authentication"])

def _set_session_cookie(response: Response, session_id: str):
    is_secure = settings.COOKIE_SECURE or (settings.ENVIRONMENT == "production")
    samesite = "none" if is_secure else settings.COOKIE_SAMESITE
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=session_id,
        max_age=settings.SESSION_TTL_SECONDS,
        httponly=settings.COOKIE_HTTPONLY,
        secure=is_secure,
        samesite=samesite,
        path="/"
    )

def _clear_session_cookie(response: Response):
    is_secure = settings.COOKIE_SECURE or (settings.ENVIRONMENT == "production")
    samesite = "none" if is_secure else settings.COOKIE_SAMESITE
    response.delete_cookie(
        key=settings.SESSION_COOKIE_NAME,
        path="/",
        httponly=settings.COOKIE_HTTPONLY,
        secure=is_secure,
        samesite=samesite
    )

@router.post(
    "/register",
    response_model=ApiResponse[Dict[str, Any]],
    dependencies=[Depends(rate_limit("register", 10, 600))]
)
async def register(
    req: RegisterRequest,
    response: Response,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    user_repo = UserRepository(db)
    pwd_hash = hash_password(req.password)
    user_doc = await user_repo.create_user(
        name=req.name,
        email=req.email,
        password_hash=pwd_hash,
        role="farmer"
    )

    user_id = str(user_doc["_id"])
    session_id = await SessionService.create_session(user_id=user_id, role="farmer")
    _set_session_cookie(response, session_id)
    csrf_token = generate_csrf_token(session_id)

    profile = {
        "user": {
            "id": user_id,
            "name": user_doc["name"],
            "email": user_doc["email"],
            "role": user_doc["role"],
            "isActive": user_doc["isActive"],
            "createdAt": user_doc["createdAt"].isoformat() if hasattr(user_doc["createdAt"], "isoformat") else str(user_doc["createdAt"])
        },
        "csrfToken": csrf_token,
        "sessionId": session_id
    }
    return ApiResponse(data=profile)

@router.post(
    "/login",
    response_model=ApiResponse[Dict[str, Any]],
    dependencies=[Depends(rate_limit("login", settings.RATE_LIMIT_LOGIN_MAX_ATTEMPTS, settings.RATE_LIMIT_LOGIN_WINDOW_SECONDS))]
)
async def login(
    req: LoginRequest,
    response: Response,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(req.email)
    
    # Generic error message to prevent account enumeration
    generic_auth_err = "Invalid email or password"

    if not user:
        raise AuthenticationError(generic_auth_err)

    if not verify_password(req.password, user.get("passwordHash", "")):
        raise AuthenticationError(generic_auth_err)

    if not user.get("isActive", True):
        raise AuthenticationError("Account is suspended or deactivated. Contact support.")

    user_id = str(user["_id"])
    role = user.get("role", "farmer")
    session_id = await SessionService.create_session(user_id=user_id, role=role)
    _set_session_cookie(response, session_id)
    csrf_token = generate_csrf_token(session_id)

    profile = {
        "user": {
            "id": user_id,
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "isActive": user["isActive"],
            "createdAt": user["createdAt"].isoformat() if hasattr(user["createdAt"], "isoformat") else str(user["createdAt"])
        },
        "csrfToken": csrf_token,
        "sessionId": session_id
    }
    return ApiResponse(data=profile)

@router.post(
    "/demo",
    response_model=ApiResponse[Dict[str, Any]]
)
async def demo_login(
    response: Response,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    user_repo = UserRepository(db)
    demo_email = "demo@krishiguard.ai"
    user = await user_repo.get_by_email(demo_email)

    if not user:
        pwd_hash = hash_password("DemoFarmer2026!")
        user = await user_repo.create_user(
            name="Demo Farmer (Anil)",
            email=demo_email,
            password_hash=pwd_hash,
            role="farmer"
        )
        user_id = str(user["_id"])
        
        # Seed 2 realistic demo farms for immediate exploring
        from backend.app.repositories.farm_repo import FarmRepository
        farm_repo = FarmRepository(db)
        await farm_repo.create_farm({
            "ownerUserId": user_id,
            "name": "Sahyadri Vineyards",
            "cropType": "Grapes",
            "soilType": "Black Cotton Soil",
            "irrigationMethod": "Drip Irrigation",
            "latitude": 18.5204,
            "longitude": 73.8567,
            "acreage": 8.5,
            "plantingDate": "2024-01-15",
            "status": "active"
        })
        await farm_repo.create_farm({
            "ownerUserId": user_id,
            "name": "Krishna Valley Tomato Patch",
            "cropType": "Tomatoes",
            "soilType": "Loamy Red Soil",
            "irrigationMethod": "Sprinkler",
            "latitude": 17.6805,
            "longitude": 74.0183,
            "acreage": 4.2,
            "plantingDate": "2024-03-01",
            "status": "active"
        })
    else:
        user_id = str(user["_id"])

    session_id = await SessionService.create_session(user_id=user_id, role="farmer")
    _set_session_cookie(response, session_id)
    csrf_token = generate_csrf_token(session_id)

    profile = {
        "user": {
            "id": user_id,
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "isActive": user.get("isActive", True),
            "createdAt": user["createdAt"].isoformat() if hasattr(user["createdAt"], "isoformat") else str(user["createdAt"])
        },
        "csrfToken": csrf_token,
        "sessionId": session_id
    }
    return ApiResponse(data=profile)

@router.post("/logout", response_model=ApiResponse[bool])
async def logout(
    request: Request,
    response: Response
):
    session_id = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not session_id:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_id = auth_header.split(" ", 1)[1].strip()
        elif request.headers.get("X-Session-ID"):
            session_id = request.headers.get("X-Session-ID")

    if session_id:
        await SessionService.revoke_session(session_id)
    _clear_session_cookie(response)
    return ApiResponse(data=True)

@router.get("/me", response_model=ApiResponse[Dict[str, Any]])
async def get_current_user_profile(
    user: Dict[str, Any] = Depends(get_current_user)
):
    session_id = user.get("_current_session_id", "")
    csrf_token = generate_csrf_token(session_id)
    profile = {
        "user": {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "isActive": user["isActive"],
            "createdAt": user["createdAt"].isoformat()
        },
        "csrfToken": csrf_token
    }
    return ApiResponse(data=profile)

@router.post(
    "/password/change",
    response_model=ApiResponse[bool],
    dependencies=[Depends(verify_csrf)]
)
async def change_password(
    req: PasswordChangeRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if not verify_password(req.current_password, user.get("passwordHash", "")):
        raise AuthenticationError("Current password incorrect.")

    new_hash = hash_password(req.new_password)
    user_repo = UserRepository(db)
    await user_repo.update_password(str(user["_id"]), new_hash)
    return ApiResponse(data=True)

@router.post(
    "/password-reset/request",
    response_model=ApiResponse[Dict[str, str]],
    dependencies=[Depends(rate_limit("password_reset", 3, 900))]
)
async def password_reset_request(
    req: PasswordResetRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(req.email)
    # Always return a generic success message so we don't leak user existence
    msg = "If an account exists with this email address, password reset instructions have been dispatched."
    return ApiResponse(data={"message": msg})
