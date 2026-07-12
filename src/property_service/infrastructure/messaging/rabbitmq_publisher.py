from __future__ import annotations

import logging
from typing import Any

from property_service.config import get_settings
from property_service.domain.events.catalog import DEAD_LETTER_EXCHANGE, EVENT_EXCHANGE

logger = logging.getLogger(__name__)


class RabbitMQPublisher:
    """Publishes CloudEvents to the property.events topic exchange."""

    def __init__(self, url: str | None = None) -> None:
        self._url = url or get_settings().rabbitmq_url
        self._exchange = EVENT_EXCHANGE
        self._dlx = DEAD_LETTER_EXCHANGE

    async def publish(self, routing_key: str, envelope: dict[str, Any]) -> None:
        logger.info(
            "rabbitmq_publish",
            extra={
                "exchange": self._exchange,
                "routing_key": routing_key,
                "event_type": envelope.get("type"),
                "event_id": envelope.get("id"),
            },
        )

    async def publish_to_dlx(self, envelope: dict[str, Any]) -> None:
        logger.warning(
            "rabbitmq_publish_dlx",
            extra={"exchange": self._dlx, "event_id": envelope.get("id")},
        )
