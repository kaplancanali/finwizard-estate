from __future__ import annotations

from dataclasses import dataclass

LAYERS: tuple[str, ...] = ("domain", "application", "infrastructure", "presentation", "di", "config", "shared")

# (source_layer, forbidden_target_layer)
FORBIDDEN_LAYER_IMPORTS: tuple[tuple[str, str], ...] = (
    ("domain", "infrastructure"),
    ("domain", "presentation"),
    ("domain", "application"),
    ("application", "presentation"),
    ("infrastructure", "presentation"),
)

# Celery tasks must not depend on HTTP/API layer.
CELERY_FORBIDDEN_PREFIXES: tuple[str, ...] = (
    "property_service.presentation.api",
    "property_service.presentation.schemas",
)


@dataclass(frozen=True)
class LayerViolation:
    module: str
    imported: str
    rule: str


def module_layer(module_name: str) -> str | None:
    if not module_name.startswith("property_service."):
        return None
    parts = module_name.split(".")
    if len(parts) < 2:
        return None
    return parts[1]
