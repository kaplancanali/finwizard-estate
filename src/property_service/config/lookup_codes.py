from __future__ import annotations

# Seeded amenity codes (migrations/versions/003_seed_lookups.py).
KNOWN_AMENITY_CODES: frozenset[str] = frozenset({
    "pool",
    "gym",
    "parking",
    "security",
    "elevator",
})
