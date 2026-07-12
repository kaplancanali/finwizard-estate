"""Seed lookup tables for property types and amenities."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None

SCHEMA = "property"


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    for code, category, display_name, is_active, sort_order in (
        ("apartment", "residential", '{"en": "Apartment", "tr": "Daire"}', True, 10),
        ("house", "residential", '{"en": "House", "tr": "Ev"}', True, 20),
        ("villa", "residential", '{"en": "Villa", "tr": "Villa"}', True, 30),
        ("land", "land", '{"en": "Land", "tr": "Arsa"}', True, 40),
        ("commercial", "commercial", '{"en": "Commercial", "tr": "Ticari"}', True, 50),
        ("office", "commercial", '{"en": "Office", "tr": "Ofis"}', True, 60),
    ):
        bind.execute(
            sa.text(
                f"""
                INSERT INTO {SCHEMA}.property_types (code, category, display_name, is_active, sort_order)
                VALUES (:code, :category, CAST(:display_name AS jsonb), :is_active, :sort_order)
                ON CONFLICT (code) DO NOTHING
                """
            ),
            {"code": code, "category": category, "display_name": display_name, "is_active": is_active, "sort_order": sort_order},
        )

    for code, category, display_name, value_type, is_active in (
        ("pool", "outdoor", '{"en": "Swimming Pool", "tr": "Havuz"}', "boolean", True),
        ("gym", "building", '{"en": "Gym", "tr": "Spor Salonu"}', "boolean", True),
        ("parking", "building", '{"en": "Parking", "tr": "Otopark"}', "boolean", True),
        ("security", "building", '{"en": "Security", "tr": "Güvenlik"}', "boolean", True),
        ("elevator", "building", '{"en": "Elevator", "tr": "Asansör"}', "boolean", True),
    ):
        bind.execute(
            sa.text(
                f"""
                INSERT INTO {SCHEMA}.amenity_definitions (code, category, display_name, value_type, is_active)
                VALUES (:code, :category, CAST(:display_name AS jsonb), :value_type, :is_active)
                ON CONFLICT (code) DO NOTHING
                """
            ),
            {"code": code, "category": category, "display_name": display_name, "value_type": value_type, "is_active": is_active},
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute(
        sa.text(
            f"DELETE FROM {SCHEMA}.property_types WHERE code IN "
            "('apartment', 'house', 'villa', 'land', 'commercial', 'office')"
        )
    )
    op.execute(
        sa.text(
            f"DELETE FROM {SCHEMA}.amenity_definitions WHERE code IN "
            "('pool', 'gym', 'parking', 'security', 'elevator')"
        )
    )
