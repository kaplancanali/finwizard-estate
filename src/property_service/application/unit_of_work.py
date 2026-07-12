from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType

from property_service.domain.repositories.outbox_repository import IOutboxRepository
from property_service.domain.repositories.property_repository import IPropertyRepository
from property_service.domain.repositories.property_version_repository import IPropertyVersionRepository


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
