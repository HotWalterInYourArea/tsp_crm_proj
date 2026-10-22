import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClientBase(BaseModel):
    name: str = Field(max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=16)
    responsible_user_id: uuid.UUID


class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    responsible_user_id: uuid.UUID | None = None

class ClientRead(ClientBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    date_created: datetime
    date_updated: datetime