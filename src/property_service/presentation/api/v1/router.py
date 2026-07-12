from __future__ import annotations

from fastapi import APIRouter

from property_service.presentation.api.v1 import (
    bulk_operations,
    properties,
    property_documents,
    property_history,
    property_images,
    property_metadata,
    property_search,
    property_statistics,
    property_versions,
)
from property_service.presentation.api.v1.lookups import router as lookups_router

api_v1_router = APIRouter()

api_v1_router.include_router(property_search.router)
api_v1_router.include_router(bulk_operations.router)
api_v1_router.include_router(properties.router)
api_v1_router.include_router(property_statistics.router)
api_v1_router.include_router(property_images.router)
api_v1_router.include_router(property_documents.router)
api_v1_router.include_router(property_history.router)
api_v1_router.include_router(property_versions.router)
api_v1_router.include_router(property_metadata.router)
api_v1_router.include_router(lookups_router)
