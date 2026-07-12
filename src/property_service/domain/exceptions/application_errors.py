from __future__ import annotations

from property_service.domain.exceptions.base import ApplicationError


class TenantMismatchError(ApplicationError):
    def __init__(self, message: str = "Property does not belong to the current tenant") -> None:
        super().__init__(
            message=message,
            code="TENANT_MISMATCH",
            details=[],
        )


class BulkLimitExceededError(ApplicationError):
    def __init__(self, *, max_items: int, actual: int) -> None:
        super().__init__(
            message=f"Bulk operation exceeds maximum of {max_items} items (got {actual})",
            code="BULK_LIMIT_EXCEEDED",
            details=[],
        )


class ImportJobFailedError(ApplicationError):
    def __init__(self, job_id: str, message: str = "Bulk import job failed") -> None:
        super().__init__(
            message=message,
            code="IMPORT_JOB_FAILED",
            details=[],
        )


class IdempotencyConflictError(ApplicationError):
    def __init__(self, message: str = "Idempotency key reused with a different payload") -> None:
        super().__init__(
            message=message,
            code="IDEMPOTENCY_CONFLICT",
            details=[],
        )
