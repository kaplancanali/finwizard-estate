#!/usr/bin/env python3
"""Seed property type lookup rows (covers domain PropertyType enum)."""

from __future__ import annotations

import asyncio

from sqlalchemy import select

from property_service.infrastructure.persistence.database import get_session_factory, init_db
from property_service.infrastructure.persistence.models import PropertyTypeLookupModel


DEFAULT_TYPES = [
    ("apartment", "residential", {"en": "Apartment", "tr": "Daire"}),
    ("villa", "residential", {"en": "Villa", "tr": "Villa"}),
    ("residence", "residential", {"en": "Residence", "tr": "Residence"}),
    ("detached_house", "residential", {"en": "Detached House", "tr": "Müstakil Ev"}),
    ("house", "residential", {"en": "House", "tr": "Ev"}),
    ("land", "land", {"en": "Land", "tr": "Arsa"}),
    ("commercial", "commercial", {"en": "Commercial", "tr": "Ticari"}),
    ("office", "commercial", {"en": "Office", "tr": "Ofis"}),
    ("store", "commercial", {"en": "Store", "tr": "Dükkan"}),
    ("warehouse", "industrial", {"en": "Warehouse", "tr": "Depo"}),
    ("factory", "industrial", {"en": "Factory", "tr": "Fabrika"}),
    ("industrial", "industrial", {"en": "Industrial", "tr": "Sanayi"}),
    ("hotel", "hospitality", {"en": "Hotel", "tr": "Otel"}),
    ("farm", "agricultural", {"en": "Farm", "tr": "Çiftlik"}),
    ("mixed_project", "mixed_use", {"en": "Mixed Project", "tr": "Karma Proje"}),
    ("other", "residential", {"en": "Other", "tr": "Diğer"}),
]


async def seed() -> None:
    await init_db()
    factory = get_session_factory()
    async with factory() as session:
        for code, category, display_name in DEFAULT_TYPES:
            exists = await session.scalar(
                select(PropertyTypeLookupModel).where(PropertyTypeLookupModel.code == code)
            )
            if exists:
                continue
            session.add(
                PropertyTypeLookupModel(code=code, category=category, display_name=display_name)
            )
        await session.commit()
    print(f"Seeded {len(DEFAULT_TYPES)} property types (idempotent).")


if __name__ == "__main__":
    asyncio.run(seed())
