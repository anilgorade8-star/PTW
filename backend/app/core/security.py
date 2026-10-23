import secrets
import hashlib
import hmac
import base64
from typing import Optional
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from backend.app.core.config import settings

# Initialize Argon2id password hasher with secure recommended parameters
# memory_cost=65536 (64MB), time_cost=2, parallelism=1
hasher = PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=1,
    hash_len=32
)

def hash_password(password: str) -> str:
    """Hash password using Argon2id."""
    return hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against Argon2id hash."""
    try:
        return hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False

def generate_session_id() -> str:
    """Generate a cryptographically secure random session ID."""
    return secrets.token_urlsafe(32)

def hash_session_id(session_id: str) -> str:
    """
    Produce a SHA-256 hash of the session ID.
    The raw session ID is stored only in the farmer's HttpOnly cookie.
    Redis stores session data keyed by the hash: kg:session:v1:{hash}
    """
    return hashlib.sha256(session_id.encode("utf-8")).hexdigest()

def generate_csrf_token(session_id: str) -> str:
    """
    Generate an HMAC-SHA256 CSRF token tied to the session and CSRF_SECRET.
    """
    msg = session_id.encode("utf-8")
    key = settings.CSRF_SECRET.encode("utf-8")
    sig = hmac.new(key, msg, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(sig).decode("utf-8").rstrip("=")

def verify_csrf_token(session_id: str, csrf_token: str) -> bool:
    """
    Constant-time comparison of expected vs provided CSRF token.
    """
    expected = generate_csrf_token(session_id)
    return hmac.compare_digest(expected, csrf_token)
