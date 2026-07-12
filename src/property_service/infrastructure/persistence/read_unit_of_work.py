from __future__ import annotations

from contextlib import asynccontextmanager

from property_service.infrastructure.persistence.repositories.search_repository import SqlAlchemySearchRepository


@asynccontextmanager
async def search_unit_of_work():
    """Read-side session scope for CQRS search repository (separate from write UoW)."""
    from property_service.infrastructure.persistence.database import get_session_factory

    factory = get_session_factory()
    async with factory() as session:
        try:
            yield SqlAlchemySearchRepository(session)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
