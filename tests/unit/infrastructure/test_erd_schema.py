"""Validate ORM metadata against the architecture ERD."""

from __future__ import annotations

import importlib

import pytest

from property_service.infrastructure.persistence.database import Base, PROPERTY_SCHEMA
from property_service.infrastructure.persistence.erd import ALL_ERD_TABLES, ORM_TABLE_TO_MODEL, PROPERTY_ERD


@pytest.mark.parametrize("table_name", sorted(ALL_ERD_TABLES))
def test_erd_table_has_orm_model(table_name: str) -> None:
    model_name = ORM_TABLE_TO_MODEL[table_name]
    models = importlib.import_module("property_service.infrastructure.persistence.models")
    assert hasattr(models, model_name), f"Missing ORM model {model_name} for {table_name}"


def test_all_erd_tables_registered_in_metadata() -> None:
    import property_service.infrastructure.persistence.models  # noqa: F401

    registered = {table.name for table in Base.metadata.sorted_tables}
    missing = ALL_ERD_TABLES - registered
    assert not missing, f"Tables in ERD but not in SQLAlchemy metadata: {missing}"


def test_property_schema_on_postgres_tables() -> None:
    import property_service.infrastructure.persistence.models  # noqa: F401

    for table in Base.metadata.sorted_tables:
        assert table.schema == PROPERTY_SCHEMA


@pytest.mark.parametrize("relationship", PROPERTY_ERD)
def test_erd_child_table_exists(relationship) -> None:
    import property_service.infrastructure.persistence.models  # noqa: F401

    child = relationship.child
    if child == "outbox_events":
        return
    tables = {t.name for t in Base.metadata.sorted_tables}
    assert child in tables


def test_property_model_relationships_cover_aggregate_children() -> None:
    from property_service.infrastructure.persistence.models import PropertyModel

    relationship_names = {rel.key for rel in PropertyModel.__mapper__.relationships}
    expected = {
        "address",
        "parcel",
        "building",
        "features",
        "metadata_row",
        "listing",
        "amenities",
        "images",
        "videos",
        "documents",
        "ownership",
        "ownership_history",
        "tags",
        "external_sources",
        "price_history",
        "status_history",
        "versions",
        "audit_logs",
        "property_type_ref",
    }
    missing = expected - relationship_names
    assert not missing, f"PropertyModel missing relationships: {missing}"
