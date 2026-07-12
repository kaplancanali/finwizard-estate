from __future__ import annotations

from property_service.domain.exceptions.base import PresentationError


class AuthenticationError(PresentationError):
    def __init__(self, message: str = "Invalid or missing authentication") -> None:
        super().__init__(message=message, code="UNAUTHORIZED")


class AuthorizationError(PresentationError):
    def __init__(self, message: str = "Forbidden", *, code: str = "FORBIDDEN") -> None:
        super().__init__(message=message, code=code)


class RateLimitExceededError(PresentationError):
    def __init__(self, message: str = "Too many requests", *, retry_after: int = 60) -> None:
        super().__init__(message=message, code="RATE_LIMIT_EXCEEDED")
        self.retry_after = retry_after


# Backward-compatible alias (pre-doc-11 name).
ForbiddenError = AuthorizationError
