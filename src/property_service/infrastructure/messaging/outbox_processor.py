from __future__ import annotations

import logging
from uuid import UUID

from property_service.domain.events.catalog import MAX_OUTBOX_RETRIES, OUTBOX_BATCH_SIZE
from property_service.infrastructure.messaging.cloudevents import build_cloudevent_from_outbox
from property_service.infrastructure.messaging.event_serializer import EventSerializer
from property_service.infrastructure.messaging.rabbitmq_publisher import RabbitMQPublisher
from property_service.infrastructure.persistence.unit_of_work import unit_of_work

logger = logging.getLogger(__name__)


class OutboxProcessor:
    def __init__(
        self,
        publisher: RabbitMQPublisher | None = None,
        serializer: EventSerializer | None = None,
        *,
        batch_size: int = OUTBOX_BATCH_SIZE,
        max_retries: int = MAX_OUTBOX_RETRIES,
    ) -> None:
        self._publisher = publisher or RabbitMQPublisher()
        self._serializer = serializer or EventSerializer()
        self._batch_size = batch_size
        self._max_retries = max_retries

    async def process_batch(self, batch_size: int | None = None) -> int:
        published = 0
        limit = batch_size or self._batch_size
        async with unit_of_work() as uow:
            pending = await uow.outbox.get_pending(batch_size=limit)
            for event in pending:
                routing_key = event.routing_key or str(event.metadata.get("routing_key", "property.unknown.v1"))
                envelope = build_cloudevent_from_outbox(
                    event_id=event.id,
                    event_type=event.event_type,
                    payload=event.payload,
                    metadata=event.metadata,
                    occurred_at=str(event.metadata.get("occurred_at", "")),
                    aggregate_id=event.aggregate_id,
                )
                try:
                    await self._publisher.publish(routing_key, envelope)
                    await uow.outbox.mark_published([event.id])
                    published += 1
                except Exception:
                    next_retry = event.retry_count + 1
                    await uow.outbox.mark_failed(event.id)
                    if next_retry >= self._max_retries:
                        await self._publisher.publish_to_dlx(envelope)
                    logger.exception("outbox_publish_failed", extra={"event_id": str(event.id)})

        logger.info("outbox_batch_processed", extra={"count": published})
        return published
