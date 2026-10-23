from typing import Optional, Dict, Any, Callable
from fastapi import Request, Depends, Header
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.app.core.config import settings
from backend.app.core.errors import AuthenticationError, AuthorizationError
from backend.app.core.security import verify_csrf_token
from backend.app.database import get_db
from backend.app.repositories.user_repo import UserRepository
from backend.app.services.session_service import SessionService

async def get_current_user(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> Dict[str, Any]:
    """
    Extracts session cookie, validates against Redis, and returns the active user.
    """
    session_id = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not session_id:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_id = auth_header.split(" ", 1)[1].strip()
        elif request.headers.get("X-Session-ID"):
            session_id = request.headers.get("X-Session-ID")

    if not session_id:
        raise AuthenticationError("Authentication required. No session cookie or token found.")

    session_data = await SessionService.get_session(session_id)
    if not session_data:
        raise AuthenticationError("Session expired or invalid.")

    user_id = session_data.get("userId")
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise AuthenticationError("User account no longer exists.")

    if not user.get("isActive", True):
        raise AuthenticationError("Account is inactive or suspended.")

    # Attach session_id for CSRF verification
    user["_current_session_id"] = session_id
    return user

def require_role(allowed_roles: list[str]) -> Callable:
    async def _role_checker(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        role = user.get("role", "farmer")
        if role not in allowed_roles:
            raise AuthorizationError(f"Role '{role}' is not authorized for this action.")
        return user
    return _role_checker

async def verify_csrf(
    request: Request,
    user: Dict[str, Any] = Depends(get_current_user),
    x_csrf_token: Optional[str] = Header(None, alias="X-CSRF-Token")
):
    """
    Enforces CSRF token check on state-changing requests when authenticated via cookies.
    """
    if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        session_id = user.get("_current_session_id", "")
        if not x_csrf_token or not verify_csrf_token(session_id, x_csrf_token):
            raise AuthorizationError("Invalid or missing CSRF token.")
