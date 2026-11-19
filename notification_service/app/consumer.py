import asyncio
import json
import logging

import pika

from .config import settings
from .connection_manager import ConnectionManager
from .notification_builder import build_deal_created, build_activity_created

log = logging.getLogger(__name__)


class RabbitConsumer:


    def __init__(self, manager: ConnectionManager, loop: asyncio.AbstractEventLoop):
        self.manager = manager
        self.loop = loop
        self._conn: pika.BlockingConnection | None = None
        self._channel = None
        self._thread: asyncio.Task | None = None
        self._stop = False


    async def start(self) -> None:
        self._thread = asyncio.create_task(asyncio.to_thread(self._run_blocking))
        log.info("Rabbit consumer started in background thread")

    async def stop(self) -> None:
        self._stop = True
        try:
            if self._channel and self._channel.is_open:
                self._channel.stop_consuming()
        except Exception:
            pass
        try:
            if self._conn and self._conn.is_open:
                self._conn.close()
        except Exception:
            pass
        if self._thread:
            await self._thread

    def _run_blocking(self) -> None:
        params = pika.URLParameters(settings.rabbitmq_url)
        params.heartbeat = 30
        params.blocked_connection_timeout = 30

        while not self._stop:
            try:
                self._conn = pika.BlockingConnection(params)
                ch = self._conn.channel()
                ch.exchange_declare(
                    exchange=settings.rabbitmq_exchange,
                    exchange_type="topic",
                    durable=True,
                )
                ch.queue_declare(
                    queue=settings.rabbitmq_queue,
                    durable=True,
                    arguments={"x-dead-letter-exchange": f"{settings.rabbitmq_exchange}.dlx"},
                )
                for rk in settings.rabbitmq_routing_keys.split(","):
                    rk = rk.strip()
                    if rk:
                        ch.queue_bind(
                            queue=settings.rabbitmq_queue,
                            exchange=settings.rabbitmq_exchange,
                            routing_key=rk,
                        )

                ch.basic_qos(prefetch_count=20)
                ch.basic_consume(
                    queue=settings.rabbitmq_queue,
                    on_message_callback=self._on_message,
                )
                self._channel = ch
                log.info("Consuming from %s", settings.rabbitmq_queue)
                ch.start_consuming()
            except Exception:
                log.exception("Rabbit consumer crashed; reconnect in 5s")
                self._safe_close()
                if self._stop:
                    break
                import time
                time.sleep(5)

    def _safe_close(self) -> None:
        try:
            if self._conn and self._conn.is_open:
                self._conn.close()
        except Exception:
            pass
        self._conn = None
        self._channel = None

    def _on_message(self, ch, method, props, body) -> None:
        try:
            evt = json.loads(body)
        except Exception:
            log.exception("bad json; dropping")
            ch.basic_nack(method.delivery_tag, requeue=False)
            return

        try:
            future = asyncio.run_coroutine_threadsafe(
                self._dispatch(evt), self.loop
            )
            future.result(timeout=10)
            ch.basic_ack(method.delivery_tag)
        except Exception:
            log.exception("dispatch failed; nack (dead-letter)")
            ch.basic_nack(method.delivery_tag, requeue=False)

    async def _dispatch(self, evt: dict) -> None:
        et = evt.get("event_type")
        if et == "deal.created":
            await self._handle_deal_created(evt)
        elif et == "activity.created":
            await self._handle_activity_created(evt)
        else:
            log.warning("unknown event_type=%s", et)

    async def _handle_deal_created(self, evt: dict) -> None:
        import uuid as _uuid
        target = _uuid.UUID(evt["assigned_to"]["user_id"])
        note = build_deal_created(evt)
        n = await self.manager.send_to_user(target, note.model_dump(mode="json"))
        log.info("deal.created deal=%s -> user=%s delivered=%d",
                 evt["deal_id"], target, n)

    async def _handle_activity_created(self, evt: dict) -> None:
        import uuid as _uuid
        for s in evt.get("supervisors", []):
            uid = _uuid.UUID(s["user_id"])
            note = build_activity_created(evt, "supervisor")
            await self.manager.send_to_user(uid, note.model_dump(mode="json"))
        for a in evt.get("assignees", []):
            uid = _uuid.UUID(a["user_id"])
            note = build_activity_created(evt, "assignee")
            await self.manager.send_to_user(uid, note.model_dump(mode="json"))