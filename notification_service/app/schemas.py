import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class NotificationRecipient(BaseModel):
    user_id: uuid.UUID
    email: str | None = None
    name: str | None = None


class IncomingEvent(BaseModel):
    event_type: str
    event_id: uuid.UUID
    occurred_at: datetime
    # остальные поля — свободные
    model_config = {"extra": "allow"}


class WSNotification(BaseModel):
    """То, что уходит клиенту в WebSocket."""
    kind: Literal["notification"] = "notification"
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    title: str
    body: str
    priority: Literal["low", "normal", "high"] = "normal"

    # контекст для клиента
    deal_id: uuid.UUID | None = None
    activity_id: uuid.UUID | None = None
    actor: str | None = None          # кто инициировал
    extra: dict = Field(default_factory=dict)