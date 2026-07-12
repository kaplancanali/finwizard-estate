"""PostGIS, full-text search, and partial indexes (PostgreSQL only)."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None

SCHEMA = "property"


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS postgis"))

    op.execute(
        sa.text(
            f"""
            ALTER TABLE {SCHEMA}.properties
            ADD COLUMN IF NOT EXISTS location geography(POINT, 4326)
            """
        )
    )
    op.execute(
        sa.text(
            f"""
            ALTER TABLE {SCHEMA}.property_addresses
            ADD COLUMN IF NOT EXISTS location geography(POINT, 4326)
            """
        )
    )
    op.execute(
        sa.text(
            f"""
            ALTER TABLE {SCHEMA}.property_parcels
            ADD COLUMN IF NOT EXISTS boundary geography(POLYGON, 4326)
            """
        )
    )
    op.execute(
        sa.text(
            f"""
            ALTER TABLE {SCHEMA}.properties
            ADD COLUMN IF NOT EXISTS search_vector tsvector
            """
        )
    )

    op.execute(
        sa.text(
            f"""
            CREATE INDEX IF NOT EXISTS idx_properties_location
            ON {SCHEMA}.properties USING GIST (location)
            """
        )
    )
    op.execute(
        sa.text(
            f"""
            CREATE INDEX IF NOT EXISTS idx_property_addresses_location
            ON {SCHEMA}.property_addresses USING GIST (location)
            """
        )
    )
    op.execute(
        sa.text(
            f"""
            CREATE INDEX IF NOT EXISTS idx_property_parcels_boundary
            ON {SCHEMA}.property_parcels USING GIST (boundary)
            """
        )
    )
    op.execute(
        sa.text(
            f"""
            CREATE INDEX IF NOT EXISTS idx_properties_search_vector
            ON {SCHEMA}.properties USING GIN (search_vector)
            """
        )
    )
    op.execute(
        sa.text(
            f"""
            CREATE INDEX IF NOT EXISTS idx_properties_price
            ON {SCHEMA}.properties (sale_price)
            WHERE deleted_at IS NULL AND status IN ('active', 'listed')
            """
        )
    )
    op.execute(
        sa.text(
            f"""
            CREATE INDEX IF NOT EXISTS idx_properties_area
            ON {SCHEMA}.properties (net_area_sqm)
            WHERE deleted_at IS NULL
            """
        )
    )
    op.execute(
        sa.text(
            f"""
            CREATE INDEX IF NOT EXISTS idx_properties_tenant_status_active
            ON {SCHEMA}.properties (tenant_id, status)
            WHERE deleted_at IS NULL
            """
        )
    )
    op.execute(
        sa.text(
            f"""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_properties_tenant_slug_active
            ON {SCHEMA}.properties (tenant_id, slug)
            WHERE deleted_at IS NULL
            """
        )
    )
    op.execute(
        sa.text(
            f"""
            CREATE INDEX IF NOT EXISTS ix_property_metadata_metadata
            ON {SCHEMA}.property_metadata USING GIN ((metadata::jsonb) jsonb_path_ops)
            """
        )
    )

    op.execute(
        sa.text(
            f"""
            CREATE OR REPLACE FUNCTION {SCHEMA}.properties_search_vector_trigger()
            RETURNS trigger AS $$
            BEGIN
              NEW.search_vector :=
                setweight(to_tsvector('simple', coalesce(NEW.title, '')), 'A') ||
                setweight(to_tsvector('simple', coalesce(NEW.description, '')), 'B') ||
                setweight(
                  to_tsvector(
                    'simple',
                    coalesce(NEW.province, '') || ' ' ||
                    coalesce(NEW.district, '') || ' ' ||
                    coalesce(NEW.neighborhood, '')
                  ),
                  'C'
                );
              RETURN NEW;
            END
            $$ LANGUAGE plpgsql
            """
        )
    )
    op.execute(
        sa.text(
            f"""
            DROP TRIGGER IF EXISTS trg_properties_search_vector ON {SCHEMA}.properties
            """
        )
    )
    op.execute(
        sa.text(
            f"""
            CREATE TRIGGER trg_properties_search_vector
            BEFORE INSERT OR UPDATE OF title, description, province, district, neighborhood
            ON {SCHEMA}.properties
            FOR EACH ROW
            EXECUTE FUNCTION {SCHEMA}.properties_search_vector_trigger()
            """
        )
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute(sa.text(f"DROP TRIGGER IF EXISTS trg_properties_search_vector ON {SCHEMA}.properties"))
    op.execute(sa.text(f"DROP FUNCTION IF EXISTS {SCHEMA}.properties_search_vector_trigger()"))
    for idx in (
        "ix_property_metadata_metadata",
        "uq_properties_tenant_slug_active",
        "idx_properties_tenant_status_active",
        "idx_properties_area",
        "idx_properties_price",
        "idx_properties_search_vector",
        "idx_property_parcels_boundary",
        "idx_property_addresses_location",
        "idx_properties_location",
    ):
        op.execute(sa.text(f"DROP INDEX IF EXISTS {SCHEMA}.{idx}"))

    op.execute(sa.text(f"ALTER TABLE {SCHEMA}.properties DROP COLUMN IF EXISTS search_vector"))
    op.execute(sa.text(f"ALTER TABLE {SCHEMA}.property_parcels DROP COLUMN IF EXISTS boundary"))
    op.execute(sa.text(f"ALTER TABLE {SCHEMA}.property_addresses DROP COLUMN IF EXISTS location"))
    op.execute(sa.text(f"ALTER TABLE {SCHEMA}.properties DROP COLUMN IF EXISTS location"))
