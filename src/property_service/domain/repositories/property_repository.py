from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from property_service.domain.aggregates.property import Property
from property_service.domain.entities.property_ownership import OwnershipHistoryEntry
from property_service.domain.entities.property_pricing import PriceHistoryEntry
from property_service.domain.entities.property_version import PropertyAuditLog, StatusHistoryEntry


class AuditLogEntry:
    def __init__(
        self,
        property_id: UUID,
        tenant_id: UUID,
        action: str,
        actor_id: UUID,
        *,
        actor_type: str = "user",
        changes: dict[str, object] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        correlation_id: UUID | None = None,
    ) -> None:
        self.property_id = property_id
        self.tenant_id = tenant_id
        self.action = action
        self.actor_id = actor_id
        self.actor_type = actor_type
        self.changes = changes
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.correlation_id = correlation_id


class IPropertyRepository(ABC):
    @abstractmethod
    async def get_by_id(
        self,
        property_id: UUID,
        tenant_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> Property | None: ...

    @abstractmethod
    async def get_by_code(self, property_code: str, tenant_id: UUID) -> Property | None: ...

    @abstractmethod
    async def get_by_slug(self, slug: str, tenant_id: UUID) -> Property | None: ...

    @abstractmethod
    async def exists_by_listing(self, provider: str, listing_id: str) -> bool: ...

    @abstractmethod
    async def add(self, property: Property) -> Property: ...

    @abstractmethod
    async def update(self, property: Property) -> Property:
        """Raises ConcurrencyConflictError if version mismatch."""
        ...

    @abstractmethod
    async def soft_delete(self, property_id: UUID, tenant_id: UUID) -> None: ...

    @abstractmethod
    async def restore(self, property_id: UUID, tenant_id: UUID) -> Property: ...

    @abstractmethod
    async def bulk_soft_delete(self, property_ids: list[UUID], tenant_id: UUID) -> int: ...

    @abstractmethod
    async def get_price_history(
        self,
        property_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[PriceHistoryEntry], int]: ...

    @abstractmethod
    async def get_status_history(
        self,
        property_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[StatusHistoryEntry], int]: ...

    @abstractmethod
    async def get_ownership_history(
        self,
        property_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[OwnershipHistoryEntry], int]: ...

    @abstractmethod
    async def get_audit_logs(
        self,
        property_id: UUID,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[PropertyAuditLog], int]: ...

    @abstractmethod
    async def append_audit_log(self, entry: AuditLogEntry) -> None: ...
