import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class NotificationRecipient(BaseModel):
    user_id: uuid.UUID
    email: str | None = None
    name: str | None = None


class DealCreatedEvent(BaseModel):
    event_type: Literal["deal.created"] = "deal.created"
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    occurred_at: datetime = Field(default_factory=datetime.utcnow)

    deal_id: uuid.UUID
    deal_name: str
    budget: int | None = None

    created_by: NotificationRecipient
    assigned_to: NotificationRecipient
    main_client_id: uuid.UUID | None = None
    pipeline_id: uuid.UUID
    pipeline_stage_id: uuid.UUID
    supervisor_ids: list[uuid.UUID] = Field(default_factory=list)


class ActivityCreatedEvent(BaseModel):
    event_type: Literal["activity.created"] = "activity.created"
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    occurred_at: datetime = Field(default_factory=datetime.utcnow)

    activity_id: uuid.UUID
    activity_name: str
    activity_type: str | None = None
    due_at: datetime | None = None

    deal_id: uuid.UUID
    deal_name: str

    author: NotificationRecipient
    assignees: list[NotificationRecipient]
    supervisors: list[NotificationRecipient]