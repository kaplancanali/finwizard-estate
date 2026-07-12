from __future__ import annotations

from property_service.domain.exceptions.base import DomainError, ErrorDetail, PropertyServiceError


class ValidationError(DomainError):
    def __init__(
        self,
        message: str,
        *,
        code: str = "VALIDATION_ERROR",
        field: str | None = None,
        details: list[ErrorDetail] | None = None,
    ) -> None:
        error_details = list(details or [])
        if field and not error_details:
            error_details.append(ErrorDetail(field=field, message=message, code=code))
        super().__init__(message=message, code=code, details=error_details)
