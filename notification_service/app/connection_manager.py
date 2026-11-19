import asyncio
import logging
import uuid
from collections import defaultdict
from typing import Any

from fastapi import WebSocket

log = logging.getLogger(__name__)


class ConnectionManager:

    def __init__(self) -> None:
        self._connections: dict[uuid.UUID, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, user_id: uuid.UUID, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._connections[user_id].add(ws)
        log.info("WS connected user=%s total=%d", user_id, len(self._connections[user_id]))

    async def disconnect(self, user_id: uuid.UUID, ws: WebSocket) -> None:
        async with self._lock:
            bucket = self._connections.get(user_id)
            if bucket:
                bucket.discard(ws)
                if not bucket:
                    self._connections.pop(user_id, None)
        log.info("WS disconnected user=%s", user_id)

    async def send_to_user(self, user_id: uuid.UUID, payload: dict[str, Any]) -> int:
        async with self._lock:
            sockets = list(self._connections.get(user_id, ()))
        delivered = 0
        for ws in sockets:
            try:
                await ws.send_json(payload)
                delivered += 1
            except Exception:
                log.exception("send failed; dropping socket user=%s", user_id)
                async with self._lock:
                    self._connections.get(user_id, set()).discard(ws)
        return delivered

    def online_users(self) -> list[uuid.UUID]:
        return list(self._connections.keys())