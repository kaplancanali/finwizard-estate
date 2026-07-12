from __future__ import annotations

from dataclasses import dataclass

from property_service.application.handlers.command_handlers import (
    ChangePropertyStatusHandler,
    CreatePropertyHandler,
    DeletePropertyHandler,
    RegisterFromSourceHandler,
    RestorePropertyHandler,
    UpdatePropertyHandler,
)
from property_service.application.handlers.query_handlers import (
    GetNearbyPropertiesHandler,
    GetPropertyHandler,
    GetPropertyHistoryHandler,
    GetPropertyStatisticsHandler,
    GetPropertyVersionsHandler,
    SearchPropertiesHandler,
)


@dataclass
class HandlerRegistry:
    create_property: CreatePropertyHandler
    update_property: UpdatePropertyHandler
    delete_property: DeletePropertyHandler
    restore_property: RestorePropertyHandler
    change_status: ChangePropertyStatusHandler
    register_from_source: RegisterFromSourceHandler
    get_property: GetPropertyHandler
    search_properties: SearchPropertiesHandler
    get_nearby: GetNearbyPropertiesHandler
    get_statistics: GetPropertyStatisticsHandler
    get_history: GetPropertyHistoryHandler
    get_versions: GetPropertyVersionsHandler
