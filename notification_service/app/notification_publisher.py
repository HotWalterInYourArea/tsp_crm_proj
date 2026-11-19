import json
import logging
import threading
import uuid
from typing import Any

import pika
from pika.exchange_type import ExchangeType

from api_service.core.config import settings
from api_service.schemas.notifications_schema import (
    DealCreatedEvent,
    ActivityCreatedEvent,
    NotificationRecipient,
)
from db_service.models.deal import Deal
from db_service.models.user import User

logger = logging.getLogger(__name__)


class NotificationPublisher:

    _instance: "NotificationPublisher | None" = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, url: str | None = None, exchange: str | None = None,
                 exchange_type: str = "topic"):
        if self._initialized:
            return
        self.url = url or settings.rabbitmq_url
        self.exchange = exchange or settings.rabbitmq_exchange
        self.exchange_type = exchange_type or settings.rabbitmq_exchange_type
        self._conn: pika.BlockingConnection | None = None
        self._channel: pika.adapters.blocking_connection.BlockingChannel | None = None
        self._chan_lock = threading.Lock()
        self._initialized = True

    def _connect(self) -> None:
        params = pika.URLParameters(self.url)
        self._conn = pika.BlockingConnection(params)
        self._channel = self._conn.channel()
        self._channel.exchange_declare(
            exchange=self.exchange,
            exchange_type=ExchangeType(self.exchange_type),
            durable=True,
        )

    def _ensure_channel(self):
        if (
            self._channel is None
            or not self._channel.is_open
            or self._conn is None
            or self._conn.is_closed
        ):
            self._connect()
        return self._channel

    def close(self) -> None:
        with self._chan_lock:
            try:
                if self._conn and self._conn.is_open:
                    self._conn.close()
            except Exception:
                pass
            self._conn = None
            self._channel = None

    def publish(self, routing_key: str, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        with self._chan_lock:
            try:
                ch = self._ensure_channel()
                ch.basic_publish(
                    exchange=self.exchange,
                    routing_key=routing_key,
                    body=body,
                    properties=pika.BasicProperties(
                        content_type="application/json",
                        delivery_mode=2,   # persistent
                        message_id=str(payload.get("event_id", uuid.uuid4())),
                        timestamp=None,
                    ),
                )
                logger.info("Published %s (%s bytes)", routing_key, len(body))
            except Exception:
                logger.exception("Rabbit publish failed; resetting connection")
                self._conn = None
                self._channel = None
                raise

    def publish_deal_created(self, deal: Deal, creator: User) -> None:
        if deal.assigned_by is None:
            logger.warning("Deal %s has no assignee; skipping notify", deal.id)
            return

        event = DealCreatedEvent(
            deal_id=deal.id,
            deal_name=deal.name,
            budget=deal.budget,
            created_by=self._recipient(creator),
            assigned_to=self._recipient(deal.assigned_by),
            main_client_id=deal.main_client_id,
            pipeline_id=deal.pipeline_id,
            pipeline_stage_id=deal.pipeline_stage_id,
            supervisor_ids=[u.id for u in (deal.supervised_by or [])],
        )
        self.publish(settings.rk_deal_created, event.model_dump(mode="json"))

    def publish_activity_created(
        self,
        activity_id: uuid.UUID,
        activity_name: str,
        activity_type: str | None,
        due_at,
        deal: Deal,
        author: User,
    ) -> None:
        recipients_supervisors = [self._recipient(u) for u in (deal.supervised_by or [])]
        assignees = []
        if deal.assigned_by is not None:
            assignees.append(self._recipient(deal.assigned_by))

        if not recipients_supervisors and not assignees:
            logger.info("Activity %s has no recipients; skipping notify", activity_id)
            return

        event = ActivityCreatedEvent(
            activity_id=activity_id,
            activity_name=activity_name,
            activity_type=activity_type,
            due_at=due_at,
            deal_id=deal.id,
            deal_name=deal.name,
            author=self._recipient(author),
            assignees=assignees,
            supervisors=recipients_supervisors,
        )
        self.publish(settings.rk_activity_created, event.model_dump(mode="json"))

    @staticmethod
    def _recipient(u: User | None) -> NotificationRecipient:
        if u is None:
            raise ValueError("Recipient user is None")
        return NotificationRecipient(
            user_id=u.id,
            email=getattr(u, "email", None),
            name=getattr(u, "name", None),
        )


publisher = NotificationPublisher()