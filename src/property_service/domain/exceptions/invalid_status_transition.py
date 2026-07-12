from __future__ import annotations

from property_service.domain.exceptions.base import DomainError


class InvalidStatusTransitionError(DomainError):
    def __init__(self, current: str, target: str) -> None:
        super().__init__(
            message=f"Cannot transition from '{current}' to '{target}'",
            code="INVALID_STATUS_TRANSITION",
        )
