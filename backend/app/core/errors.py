from fastapi import HTTPException, status
from typing import Optional, Any, Dict

class KrishiGuardException(Exception):
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details

class AuthenticationError(KrishiGuardException):
    def __init__(self, message: str = "Invalid credentials or session expired", details: Optional[Any] = None):
        super().__init__(message=message, code="AUTH_FAILED", details=details)

class AuthorizationError(KrishiGuardException):
    def __init__(self, message: str = "You do not have permission to access this resource", details: Optional[Any] = None):
        super().__init__(message=message, code="FORBIDDEN", details=details)

class NotFoundError(KrishiGuardException):
    def __init__(self, resource: str, resource_id: str):
        super().__init__(message=f"{resource} '{resource_id}' was not found", code="NOT_FOUND", details={"resource": resource, "id": resource_id})

class RateLimitExceededError(KrishiGuardException):
    def __init__(self, retry_after: int = 60):
        super().__init__(
            message=f"Rate limit exceeded. Please try again in {retry_after} seconds.",
            code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after}
        )
        self.retry_after = retry_after

class ValidationError(KrishiGuardException):
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message=message, code="VALIDATION_FAILED", details=details)

class ConflictError(KrishiGuardException):
    def __init__(self, message: str = "A conflicting resource already exists"):
        super().__init__(message=message, code="CONFLICT")

class ExternalServiceError(KrishiGuardException):
    def __init__(self, service: str, message: str):
        super().__init__(message=f"External service '{service}' error: {message}", code="SERVICE_UNAVAILABLE", details={"service": service})

class SafetyViolationError(KrishiGuardException):
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message=message, code="SAFETY_VIOLATION", details=details)
