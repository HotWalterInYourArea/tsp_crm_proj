import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ActivityTypeBase(BaseModel):
    name: str = Field(default="Новый тип дела", max_length=100)

class ActivityTypeCreate(ActivityTypeBase):
    pass

class ActivityTypeUpdate(BaseModel):
    name: str | None = None

class ActivityTypeRead(ActivityTypeBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    date_created: datetime
    date_updated: datetime


class ActivityBase(BaseModel):
    description: str | None = None
    activity_type_id: uuid.UUID | None = None
    deal_id: uuid.UUID
    user_id: uuid.UUID
    deadline_at: datetime | None = None

class ActivityCreate(ActivityBase):
    pass

class ActivityUpdate(BaseModel):
    description: str | None = None
    activity_type_id: uuid.UUID | None = None
    deal_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    deadline_at: datetime | None = None

class ActivityRead(ActivityBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    date_created: datetime
    date_updated: datetime