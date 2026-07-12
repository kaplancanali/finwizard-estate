from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from property_service.domain.exceptions import ValidationError
from property_service.domain.exceptions.base import ErrorDetail

_SCHEMA_DIR = Path(__file__).resolve().parent.parent.parent / "config" / "metadata_schemas"


class MetadataSchemaValidator:
    """Validates property metadata against per-type JSON Schema files."""

    def __init__(self, schema_dir: Path | None = None) -> None:
        self._schema_dir = schema_dir or _SCHEMA_DIR
        self._cache: dict[str, dict[str, Any]] = {}

    def validate(self, property_type: str, metadata: dict[str, Any]) -> None:
        schema = self._load_schema(property_type)
        errors = self._validate_object(metadata, schema, path="metadata")
        if errors:
            raise ValidationError(
                "Metadata validation failed",
                code="VALIDATION_ERROR",
                details=errors,
            )

    def _load_schema(self, property_type: str) -> dict[str, Any]:
        key = property_type.lower()
        if key not in self._cache:
            path = self._schema_dir / f"{key}.json"
            if not path.exists():
                path = self._schema_dir / "default.json"
            self._cache[key] = json.loads(path.read_text(encoding="utf-8"))
        return self._cache[key]

    def _validate_object(
        self,
        value: Any,
        schema: dict[str, Any],
        *,
        path: str,
    ) -> list[ErrorDetail]:
        errors: list[ErrorDetail] = []
        expected_type = schema.get("type")
        if expected_type == "object":
            if not isinstance(value, dict):
                return [ErrorDetail(field=path, message="Expected object", code="VALIDATION_ERROR")]
            properties = schema.get("properties", {})
            for key, prop_schema in properties.items():
                if key in value:
                    errors.extend(self._validate_value(value[key], prop_schema, path=f"{path}.{key}"))
            if schema.get("additionalProperties") is False:
                extra = set(value) - set(properties)
                for key in sorted(extra):
                    errors.append(
                        ErrorDetail(
                            field=f"{path}.{key}",
                            message="Additional property not allowed",
                            code="VALIDATION_ERROR",
                        )
                    )
        return errors

    def _validate_value(
        self,
        value: Any,
        schema: dict[str, Any],
        *,
        path: str,
    ) -> list[ErrorDetail]:
        errors: list[ErrorDetail] = []
        expected_type = schema.get("type")
        if expected_type == "string":
            if not isinstance(value, str):
                return [ErrorDetail(field=path, message="Expected string", code="VALIDATION_ERROR")]
            max_length = schema.get("maxLength")
            if max_length is not None and len(value) > max_length:
                errors.append(
                    ErrorDetail(
                        field=path,
                        message=f"Maximum length is {max_length}",
                        code="VALIDATION_ERROR",
                    )
                )
        elif expected_type == "number":
            if not isinstance(value, (int, float)):
                return [ErrorDetail(field=path, message="Expected number", code="VALIDATION_ERROR")]
            minimum = schema.get("minimum")
            if minimum is not None and value < minimum:
                errors.append(
                    ErrorDetail(
                        field=path,
                        message=f"Minimum value is {minimum}",
                        code="VALIDATION_ERROR",
                    )
                )
        elif expected_type == "object":
            errors.extend(self._validate_object(value, schema, path=path))
        return errors
