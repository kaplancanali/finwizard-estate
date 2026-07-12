from __future__ import annotations

from pathlib import Path

import pytest

from property_service.architecture.external_dependencies import (
    EXTERNAL_DEPENDENCIES,
    FORBIDDEN_OUTBOUND_SERVICES,
)
from property_service.architecture.import_scanner import scan_celery_tasks_for_violations, violations_for_layer
from property_service.architecture.layer_rules import FORBIDDEN_LAYER_IMPORTS
from property_service.architecture.startup import STARTUP_SEQUENCE, StartupBootstrap

PACKAGE_ROOT = Path(__file__).resolve().parents[3] / "src" / "property_service"


class TestLayerRules:
    def test_domain_has_no_outward_dependencies(self) -> None:
        violations = [
            v for v in violations_for_layer(PACKAGE_ROOT, "domain") if v.rule.startswith("domain must not")
        ]
        assert violations == [], _format_violations(violations)

    def test_application_does_not_import_presentation(self) -> None:
        violations = [
            v for v in violations_for_layer(PACKAGE_ROOT, "application") if "presentation" in v.rule
        ]
        assert violations == [], _format_violations(violations)

    def test_infrastructure_does_not_import_presentation(self) -> None:
        violations = [
            v for v in violations_for_layer(PACKAGE_ROOT, "infrastructure") if "presentation" in v.rule
        ]
        assert violations == [], _format_violations(violations)

    def test_celery_tasks_avoid_api_layer(self) -> None:
        violations = scan_celery_tasks_for_violations(PACKAGE_ROOT)
        assert violations == [], _format_violations(violations)

    def test_forbidden_rules_match_doc(self) -> None:
        assert ("domain", "application") in FORBIDDEN_LAYER_IMPORTS
        assert ("application", "presentation") in FORBIDDEN_LAYER_IMPORTS


class TestExternalDependencies:
    def test_postgresql_is_required(self) -> None:
        pg = next(dep for dep in EXTERNAL_DEPENDENCIES if dep.name == "postgresql")
        assert pg.required is True
        assert pg.fallback is None

    def test_geocoding_is_optional(self) -> None:
        geo = next(dep for dep in EXTERNAL_DEPENDENCIES if dep.name == "geocoding")
        assert geo.required is False

    def test_no_outbound_calls_to_downstream_services(self) -> None:
        assert "valuation-service" in FORBIDDEN_OUTBOUND_SERVICES


class TestStartupSequence:
    def test_startup_steps_order(self) -> None:
        assert STARTUP_SEQUENCE[:4] == (
            "load_configuration",
            "initialize_logging",
            "connect_postgresql",
            "connect_redis",
        )
        assert STARTUP_SEQUENCE[-1] == "warm_caches"

    @pytest.mark.asyncio
    async def test_bootstrap_runs_in_development(self, monkeypatch) -> None:
        monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
        monkeypatch.setenv("APP_ENV", "development")
        from property_service.config.settings import get_settings

        get_settings.cache_clear()
        from property_service.di.container import reset_container
        from property_service.infrastructure import persistence

        reset_container()
        persistence.database._engine = None
        persistence.database._session_factory = None

        import sqlalchemy as sa
        from property_service.infrastructure.persistence.database import Base, get_engine

        engine = get_engine()
        async with engine.begin() as conn:
            await conn.execute(sa.text("ATTACH DATABASE ':memory:' AS property"))
            await conn.run_sync(Base.metadata.create_all)

        from property_service.architecture.startup import bootstrap_application

        bootstrap = await bootstrap_application()
        assert "connect_postgresql" in bootstrap.completed_steps
        assert "wire_di_container" in bootstrap.completed_steps
        assert "warm_caches" in bootstrap.completed_steps

        from property_service.infrastructure.persistence.database import close_db

        await close_db()
        get_settings.cache_clear()
        reset_container()


class TestSearchCriteriaLocation:
    def test_domain_repository_imports_from_domain_queries(self) -> None:
        source = (PACKAGE_ROOT / "domain" / "repositories" / "property_search_repository.py").read_text()
        assert "domain.queries.search_criteria" in source
        assert "application.dto" not in source


def _format_violations(violations: list) -> str:
    return "\n".join(f"{v.module} -> {v.imported} ({v.rule})" for v in violations)
