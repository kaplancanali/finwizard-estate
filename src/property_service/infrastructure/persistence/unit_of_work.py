from __future__ import annotations

from contextlib import asynccontextmanager
from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession

from property_service.application.unit_of_work import IUnitOfWork
from property_service.infrastructure.persistence.repositories.outbox_repository import (
    SqlAlchemyOutboxRepository,
    SqlAlchemyVersionRepository,
)
from property_service.infrastructure.persistence.repositories.property_repository import (
    SqlAlchemyPropertyRepository,
)


class SqlAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.properties = SqlAlchemyPropertyRepository(session)
        self.versions = SqlAlchemyVersionRepository(session)
        self.outbox = SqlAlchemyOutboxRepository(session)

    @property
    def session(self) -> AsyncSession:
        return self._session

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        pass

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()


@asynccontextmanager
async def unit_of_work():
    from property_service.infrastructure.persistence.database import get_session_factory

    factory = get_session_factory()
    async with factory() as session:
        uow = SqlAlchemyUnitOfWork(session)
        try:
            yield uow
            await uow.commit()
        except Exception:
            await uow.rollback()
            raise
