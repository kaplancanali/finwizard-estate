from __future__ import annotations

from uuid import UUID

from property_service.domain.exceptions.application_errors import (
    BulkLimitExceededError,
    IdempotencyConflictError,
    ImportJobFailedError,
    TenantMismatchError,
)
from property_service.domain.exceptions.base import (
    ApplicationError,
    DomainError,
    ErrorDetail,
    InfrastructureError,
    PresentationError,
    PropertyServiceError,
)
from property_service.domain.exceptions.concurrency_conflict import ConcurrencyConflictError
from property_service.domain.exceptions.infrastructure_errors import (
    CacheError,
    DatabaseError,
    GeocodingError,
    MessagingError,
    StorageError,
)
from property_service.domain.exceptions.invalid_status_transition import InvalidStatusTransitionError
from property_service.domain.exceptions.presentation_errors import (
    AuthenticationError,
    AuthorizationError,
    ForbiddenError,
    RateLimitExceededError,
)
from property_service.domain.exceptions.property_not_found import PropertyNotFoundError
from property_service.domain.exceptions.validation_error import ValidationError


class PropertyDeletedError(DomainError):
    def __init__(self, property_id: UUID) -> None:
        super().__init__(
            message=f"Property '{property_id}' is deleted and cannot be modified",
            code="PROPERTY_DELETED",
        )


class ImmutableFieldError(DomainError):
    def __init__(self, field_name: str) -> None:
        super().__init__(
            message=f"Field '{field_name}' is immutable",
            code="IMMUTABLE_FIELD",
        )


class DuplicatePropertyError(DomainError):
    def __init__(self, message: str, *, code: str = "DUPLICATE_PROPERTY") -> None:
        super().__init__(message=message, code=code)


__all__ = [
    "ApplicationError",
    "AuthenticationError",
    "AuthorizationError",
    "BulkLimitExceededError",
    "CacheError",
    "ConcurrencyConflictError",
    "DatabaseError",
    "DomainError",
    "DuplicatePropertyError",
    "ErrorDetail",
    "ForbiddenError",
    "GeocodingError",
    "IdempotencyConflictError",
    "ImmutableFieldError",
    "ImportJobFailedError",
    "InfrastructureError",
    "InvalidStatusTransitionError",
    "MessagingError",
    "PresentationError",
    "PropertyDeletedError",
    "PropertyNotFoundError",
    "PropertyServiceError",
    "RateLimitExceededError",
    "StorageError",
    "TenantMismatchError",
    "ValidationError",
]
