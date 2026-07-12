from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from property_service.config.settings import Settings, get_settings
import sqlalchemy as sa
from property_service.infrastructure.persistence.database import Base, close_db, get_engine
from property_service.infrastructure.persistence.models import PropertyTypeLookupModel
from property_service.main import create_app


def _seed_lookup_tables(connection) -> None:
    from sqlalchemy.orm import Session

    session = Session(bind=connection)
    if session.get(PropertyTypeLookupModel, "apartment") is None:
        session.add_all(
            [
                PropertyTypeLookupModel(
                    code="apartment",
                    category="residential",
                    display_name={"en": "Apartment", "tr": "Daire"},
                ),
                PropertyTypeLookupModel(
                    code="house",
                    category="residential",
                    display_name={"en": "House", "tr": "Ev"},
                ),
            ]
        )
        session.commit()
    session.close()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def test_app(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("APP_ENV", "development")
    get_settings.cache_clear()

    from property_service.di.container import reset_container
    from property_service.infrastructure.jobs.import_job_store import reset_import_job_store
    from property_service.presentation.health import reset_startup_state

    reset_container()
    reset_import_job_store()
    reset_startup_state()

    from property_service.infrastructure import persistence
    persistence.database._engine = None
    persistence.database._session_factory = None

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.execute(sa.text("ATTACH DATABASE ':memory:' AS property"))
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_seed_lookup_tables)

    app = create_app()
    async with app.router.lifespan_context(app):
        yield app

    await close_db()
    get_settings.cache_clear()
    reset_container()


@pytest_asyncio.fixture
async def client(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


SAMPLE_PROPERTY = {
    "title": "Modern Apartment in Kadikoy",
    "description": "Spacious apartment",
    "property_type": "apartment",
    "property_category": "residential",
    "pricing": {"sale_price": 5000000, "currency": "TRY"},
    "location": {
        "country_code": "TR",
        "province": "Istanbul",
        "district": "Kadikoy",
        "latitude": 40.9876,
        "longitude": 29.0234,
    },
    "building": {"net_area_sqm": 120, "room_count": 3, "bathroom_count": 2},
}
