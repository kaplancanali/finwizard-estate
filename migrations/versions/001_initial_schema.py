"""Initial schema — all core tables in the `property` schema."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None

SCHEMA = "property"


def upgrade() -> None:
    op.execute(sa.text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}"))

    from property_service.infrastructure.persistence.database import Base
    import property_service.infrastructure.persistence.models  # noqa: F401

    bind = op.get_bind()
    Base.metadata.create_all(bind)


def downgrade() -> None:
    from property_service.infrastructure.persistence.database import Base
    import property_service.infrastructure.persistence.models  # noqa: F401

    bind = op.get_bind()
    Base.metadata.drop_all(bind)
    op.execute(sa.text(f"DROP SCHEMA IF EXISTS {SCHEMA} CASCADE"))
