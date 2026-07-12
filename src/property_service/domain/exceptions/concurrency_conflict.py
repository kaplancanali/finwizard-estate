from __future__ import annotations

from uuid import UUID

from property_service.domain.exceptions.base import DomainError


class ConcurrencyConflictError(DomainError):
    def __init__(self, property_id: UUID, expected: int, actual: int) -> None:
        super().__init__(
            message=(
                f"Property '{property_id}' was modified. "
                f"Expected version {expected}, found {actual}"
            ),
            code="CONCURRENCY_CONFLICT",
        )
