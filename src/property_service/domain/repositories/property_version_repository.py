from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from property_service.domain.entities.property_version import PropertyVersion


class IPropertyVersionRepository(ABC):
    @abstractmethod
    async def create_snapshot(
        self,
        property_id: UUID,
        version_number: int,
        snapshot: dict[str, object],
        change_summary: str,
        created_by: UUID,
    ) -> PropertyVersion: ...

    @abstractmethod
    async def get_versions(
        self,
        property_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[PropertyVersion], int]: ...

    @abstractmethod
    async def get_version(
        self,
        property_id: UUID,
        version_number: int,
    ) -> PropertyVersion | None: ...

    @abstractmethod
    async def get_latest_version_number(self, property_id: UUID) -> int: ...
