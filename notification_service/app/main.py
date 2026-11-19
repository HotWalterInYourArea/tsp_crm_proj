import asyncio
import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException

from .auth import resolve_user_id
from .consumer import RabbitConsumer
from .connection_manager import ConnectionManager

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("notification-service")

manager = ConnectionManager()
consumer: RabbitConsumer | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global consumer
    consumer = RabbitConsumer(manager, asyncio.get_running_loop())
    await consumer.start()
    try:
        yield
    finally:
        if consumer:
            await consumer.stop()


app = FastAPI(title="CRM Notification Service", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok", "online_users": [str(u) for u in manager.online_users()]}


@app.websocket("/ws/notifications")
async def ws_notifications(
    websocket: WebSocket,
    token: str | None = Query(default=None),
    user_id: str | None = Query(default=None),
):
    try:
        uid: uuid.UUID = resolve_user_id(token, user_id)
    except HTTPException as e:
        await websocket.close(code=4401, reason=str(e.detail))
        return

    await manager.connect(uid, websocket)
    try:
        await websocket.send_json({"kind": "hello", "user_id": str(uid)})
        while True:
            msg = await websocket.receive_text()
            if msg == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(uid, websocket)