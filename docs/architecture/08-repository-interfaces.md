# 8. Repository Interfaces

Repository interfaces live in the **domain layer**. Infrastructure provides SQLAlchemy implementations.

---

## IPropertyRepository

```python
from abc import ABC, abstractmethod
from uuid import UUID

from property_service.domain.aggregates.property import Property


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
    async def get_by_code(
        self,
        property_code: str,
        tenant_id: UUID,
    ) -> Property | None: ...

    @abstractmethod
    async def get_by_slug(
        self,
        slug: str,
        tenant_id: UUID,
    ) -> Property | None: ...

    @abstractmethod
    async def exists_by_listing(
        self,
        provider: str,
        listing_id: str,
    ) -> bool: ...

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
    async def bulk_soft_delete(
        self,
        property_ids: list[UUID],
        tenant_id: UUID,
    ) -> int: ...

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
    ) -> list[OwnershipHistoryEntry]: ...

    @abstractmethod
    async def append_audit_log(self, entry: AuditLogEntry) -> None: ...
```

---

## IPropertySearchRepository

Read-optimized repository for query side. Separate from write repository (CQRS-ready).

```python
from abc import ABC, abstractmethod
from uuid import UUID

from property_service.application.dto.property_search_dto import (
    PropertySearchCriteria,
    PropertySearchResult,
    NearbySearchCriteria,
    MapSearchCriteria,
    PropertyStatistics,
)


class IPropertySearchRepository(ABC):

    @abstractmethod
    async def search(
        self,
        criteria: PropertySearchCriteria,
        tenant_id: UUID,
    ) -> PropertySearchResult: ...

    @abstractmethod
    async def find_nearby(
        self,
        criteria: NearbySearchCriteria,
        tenant_id: UUID,
    ) -> PropertySearchResult: ...

    @abstractmethod
    async def map_search(
        self,
        criteria: MapSearchCriteria,
        tenant_id: UUID,
    ) -> list[MapCluster | PropertySummary]: ...

    @abstractmethod
    async def get_statistics(
        self,
        tenant_id: UUID,
        *,
        group_by: list[str] | None = None,
    ) -> PropertyStatistics: ...

    @abstractmethod
    async def count_by_tenant(self, tenant_id: UUID) -> int: ...
```

---

## IPropertyVersionRepository

```python
class IPropertyVersionRepository(ABC):

    @abstractmethod
    async def create_snapshot(
        self,
        property_id: UUID,
        version_number: int,
        snapshot: dict,
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
    async def get_latest_version_number(
        self,
        property_id: UUID,
    ) -> int: ...
```

---

## IOutboxRepository

```python
class IOutboxRepository(ABC):

    @abstractmethod
    async def add_events(self, events: list[DomainEvent]) -> None:
        """Called within UoW transaction."""
        ...

    @abstractmethod
    async def get_pending(
        self,
        *,
        batch_size: int = 100,
    ) -> list[OutboxEvent]: ...

    @abstractmethod
    async def mark_published(
        self,
        event_ids: list[UUID],
    ) -> None: ...

    @abstractmethod
    async def mark_failed(
        self,
        event_id: UUID,
        *,
        increment_retry: bool = True,
    ) -> None: ...
```

---

## IUnitOfWork

```python
from abc import ABC, abstractmethod
from types import TracebackType


class IUnitOfWork(ABC):
    properties: IPropertyRepository
    versions: IPropertyVersionRepository
    outbox: IOutboxRepository

    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork": ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
```

**Usage pattern:**

```python
async with uow:
    property = await uow.properties.get_by_id(property_id, tenant_id)
    property.update_title(new_title)
    await uow.properties.update(property)
    await uow.outbox.add_events(property.collect_events())
    await uow.commit()
```

---

## IPropertyCache (Infrastructure interface, used by application)

```python
class IPropertyCache(ABC):

    @abstractmethod
    async def get_property(self, property_id: UUID) -> dict | None: ...

    @abstractmethod
    async def set_property(self, property_id: UUID, data: dict, ttl: int) -> None: ...

    @abstractmethod
    async def invalidate_property(self, property_id: UUID) -> None: ...

    @abstractmethod
    async def get_search_results(self, cache_key: str) -> dict | None: ...

    @abstractmethod
    async def set_search_results(self, cache_key: str, data: dict, ttl: int) -> None: ...

    @abstractmethod
    async def invalidate_tenant_search(self, tenant_id: UUID) -> None: ...
```

---

## IObjectStorage

```python
class IObjectStorage(ABC):

    @abstractmethod
    async def generate_upload_url(
        self,
        key: str,
        mime_type: str,
        expires_in: int = 3600,
    ) -> str: ...

    @abstractmethod
    async def generate_download_url(
        self,
        key: str,
        expires_in: int = 3600,
    ) -> str: ...

    @abstractmethod
    async def object_exists(self, key: str) -> bool: ...

    @abstractmethod
    async def delete_object(self, key: str) -> None: ...
```

---

## IIdempotencyStore

```python
class IIdempotencyStore(ABC):

    @abstractmethod
    async def get_response(self, key: str) -> dict | None: ...

    @abstractmethod
    async def store_response(
        self,
        key: str,
        response: dict,
        ttl: int = 86400,
    ) -> None: ...

    @abstractmethod
    async def is_processing(self, key: str) -> bool: ...

    @abstractmethod
    async def mark_processing(self, key: str, ttl: int = 300) -> bool:
        """Returns False if already processing (SET NX)."""
        ...
```

---

## Implementation Notes

| Repository | Implementation | Notes |
|------------|---------------|-------|
| `IPropertyRepository` | `SqlAlchemyPropertyRepository` | Eager-loads related entities via selectinload |
| `IPropertySearchRepository` | `SqlAlchemySearchRepository` | Raw SQL for PostGIS queries; no domain entity hydration |
| `IPropertyVersionRepository` | `SqlAlchemyVersionRepository` | JSONB snapshot storage |
| `IOutboxRepository` | `SqlAlchemyOutboxRepository` | `SELECT ... FOR UPDATE SKIP LOCKED` for concurrent processors |
| `IPropertyCache` | `RedisPropertyCache` | JSON serialization |
| `IObjectStorage` | `S3ObjectStorage` | aioboto3 |
| `IIdempotencyStore` | `RedisIdempotencyStore` | SET NX pattern |

### Mapper Pattern

```
SQLAlchemy Model ←→ PropertyMapper ←→ Domain Entity (Property)
```

Mappers are stateless classes in `infrastructure/persistence/mappers/`. Repository calls mapper on read/write; domain never sees ORM models.
