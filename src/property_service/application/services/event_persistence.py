from __future__ import annotations

from property_service.application.auth_context import AuthContext
from property_service.application.unit_of_work import IUnitOfWork
from property_service.domain.aggregates.property import Property
from property_service.domain.repositories import AuditLogEntry
from property_service.infrastructure.cache.property_cache_manager import PropertyCacheManager


async def persist_domain_events(
    uow: IUnitOfWork,
    prop: Property,
    auth: AuthContext,
    *,
    cache_manager: PropertyCacheManager | None = None,
) -> None:
    events = prop.collect_events()
    if not events:
        return
    for event in events:
        if auth.correlation_id and not event.correlation_id:
            event.correlation_id = auth.correlation_id
        if not event.actor_id:
            event.actor_id = auth.user_id
    await uow.outbox.add_events(events)
    for event in events:
        await uow.properties.append_audit_log(
            AuditLogEntry(
                property_id=prop.id,
                tenant_id=auth.tenant_id,
                action=event.event_type,
                actor_id=auth.user_id,
                actor_type=auth.actor_type,
                changes=event.to_payload(),
                ip_address=auth.ip_address,
                user_agent=auth.user_agent,
                correlation_id=auth.correlation_id,
            )
        )
    if cache_manager:
        await cache_manager.handle_domain_events(events, prop)
