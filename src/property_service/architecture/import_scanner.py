from __future__ import annotations

import ast
from pathlib import Path

from property_service.architecture.layer_rules import (
    CELERY_FORBIDDEN_PREFIXES,
    FORBIDDEN_LAYER_IMPORTS,
    LayerViolation,
    module_layer,
)


def scan_package_for_violations(package_root: Path) -> list[LayerViolation]:
    violations: list[LayerViolation] = []
    for path in package_root.rglob("*.py"):
        module_name = _module_name(package_root, path)
        if module_name is None:
            continue
        source_layer = module_layer(module_name)
        if source_layer is None:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    violations.extend(_check_import(module_name, source_layer, alias.name))
            elif isinstance(node, ast.ImportFrom) and node.module:
                violations.extend(_check_import(module_name, source_layer, node.module))
    return violations


def violations_for_layer(package_root: Path, layer: str) -> list[LayerViolation]:
    prefix = f"property_service.{layer}."
    return [
        v
        for v in scan_package_for_violations(package_root)
        if v.module.startswith(prefix) or v.module == f"property_service.{layer}"
    ]


def scan_celery_tasks_for_violations(package_root: Path) -> list[LayerViolation]:
    celery_root = package_root / "infrastructure" / "celery"
    if not celery_root.exists():
        return []
    return [
        v
        for v in scan_package_for_violations(package_root)
        if v.module.startswith("property_service.infrastructure.celery")
        and _is_celery_forbidden(v.imported)
    ]


def _check_import(module_name: str, source_layer: str, imported: str) -> list[LayerViolation]:
    violations: list[LayerViolation] = []
    target_layer = module_layer(imported)
    if target_layer is None:
        return violations
    for src, forbidden in FORBIDDEN_LAYER_IMPORTS:
        if source_layer == src and target_layer == forbidden:
            violations.append(
                LayerViolation(
                    module=module_name,
                    imported=imported,
                    rule=f"{src} must not import {forbidden}",
                )
            )
    if module_name.startswith("property_service.infrastructure.celery") and _is_celery_forbidden(imported):
        violations.append(
            LayerViolation(
                module=module_name,
                imported=imported,
                rule="celery tasks must not import presentation/API layer",
            )
        )
    return violations


def _is_celery_forbidden(imported: str) -> bool:
    return any(imported.startswith(prefix) for prefix in CELERY_FORBIDDEN_PREFIXES)


def _module_name(package_root: Path, path: Path) -> str | None:
    try:
        relative = path.relative_to(package_root)
    except ValueError:
        return None
    parts = list(relative.parts)
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = parts[-1].removesuffix(".py")
    if not parts:
        return "property_service"
    return "property_service." + ".".join(parts)
