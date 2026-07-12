from __future__ import annotations

from decimal import Decimal
from enum import Enum
from uuid import UUID

from property_service.application.dto.property_create_dto import CreatePropertyDTO
from property_service.application.mappers.domain_mappers import create_property_data_from_dto
from property_service.domain.enums.source_type import SourceType
from property_service.domain.factories.property_factory import CreatePropertyData


def bulk_item_dict_to_create_property_data(
    raw: dict,
    *,
    tenant_id: UUID,
    user_id: UUID,
    source_type: SourceType,
) -> CreatePropertyData:
    """Map a bulk-import payload dict to domain create data (no presentation imports)."""
    dto = CreatePropertyDTO.from_bulk_payload(raw, tenant_id=tenant_id, user_id=user_id)
    data = create_property_data_from_dto(dto)
    data.source_type = source_type
    return data


def items_payload_to_create_property_data(
    items_payload: list[dict],
    *,
    tenant_id: UUID,
    user_id: UUID,
    source_type: SourceType,
) -> list[CreatePropertyData]:
    return [
        bulk_item_dict_to_create_property_data(
            raw,
            tenant_id=tenant_id,
            user_id=user_id,
            source_type=source_type,
        )
        for raw in items_payload
    ]


def serialize_items_payload(items_payload: list[dict]) -> list[dict]:
    return [_json_safe(item) for item in items_payload]


def _json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    return value
