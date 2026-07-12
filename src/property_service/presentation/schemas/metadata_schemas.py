from __future__ import annotations

from pydantic import BaseModel, Field


class MetadataPatchRequest(BaseModel):
    metadata: dict[str, object] | None = None
    tenant_extensions: dict[str, object] | None = None


class MetadataResponse(BaseModel):
    metadata: dict[str, object] = Field(default_factory=dict)
    tenant_extensions: dict[str, object] = Field(default_factory=dict)
    schema_version: str = "1.0"
