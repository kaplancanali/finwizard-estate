from __future__ import annotations

from uuid import UUID

from property_service.domain.exceptions.base import DomainError


class PropertyNotFoundError(DomainError):
    def __init__(self, property_id: UUID) -> None:
        super().__init__(
            message=f"Property with id '{property_id}' was not found",
            code="PROPERTY_NOT_FOUND",
        )
