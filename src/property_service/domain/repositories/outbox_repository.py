from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from property_service.domain.events.base import DomainEvent


class OutboxEvent:
    def __init__(
        self,
        id: UUID,
        aggregate_id: UUID,
        event_type: str,
        payload: dict[str, object],
        status: str = "pending",
        metadata: dict[str, object] | None = None,
        routing_key: str | None = None,
        retry_count: int = 0,
    ) -> None:
        self.id = id
        self.aggregate_id = aggregate_id
        self.event_type = event_type
        self.payload = payload
        self.status = status
        self.metadata = metadata or {}
        self.routing_key = routing_key
        self.retry_count = retry_count


class IOutboxRepository(ABC):
    @abstractmethod
    async def add_events(self, events: list[DomainEvent]) -> None: ...

    @abstractmethod
    async def get_pending(self, *, batch_size: int = 100) -> list[OutboxEvent]: ...

    @abstractmethod
    async def mark_published(self, event_ids: list[UUID]) -> None: ...

    @abstractmethod
    async def mark_failed(self, event_id: UUID, *, increment_retry: bool = True) -> None: ...
