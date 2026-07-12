from __future__ import annotations

from typing import AsyncGenerator
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import MetaData, Uuid
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from property_service.config import get_settings

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=convention)

PROPERTY_SCHEMA = "property"


def get_table_schema() -> str | None:
    """Use dedicated PostgreSQL schema; SQLite tests use attached schema or none."""
    url = get_settings().database_url
    if "sqlite" in url:
        return None
    return PROPERTY_SCHEMA


def fk_target(table: str, column: str = "id") -> str:
    schema = get_table_schema() or PROPERTY_SCHEMA
    return f"{schema}.{table}.{column}"


class Base(DeclarativeBase):
    metadata = metadata


def uuid_pk() -> Mapped:
    return mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)


_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            pool_pre_ping=True,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    factory = get_session_factory()
    async with factory() as session:
        yield session


async def init_db() -> None:
    engine = get_engine()
    async with engine.begin() as conn:
        if _is_postgres():
            await conn.execute(sa.text(f"CREATE SCHEMA IF NOT EXISTS {PROPERTY_SCHEMA}"))
        elif "sqlite" in get_settings().database_url:
            await conn.execute(sa.text(f"ATTACH DATABASE ':memory:' AS {PROPERTY_SCHEMA}"))
        await conn.run_sync(Base.metadata.create_all)


def _is_postgres() -> bool:
    return "postgresql" in get_settings().database_url


async def close_db() -> None:
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
