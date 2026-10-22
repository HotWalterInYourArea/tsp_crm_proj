import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class DepartmentBase(BaseModel):
    name: str = Field(default="Новый отдел", max_length=100)
    head_user_id: uuid.UUID | None = None


class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: str | None = None
    head_user_id: uuid.UUID | None = None

class DepartmentRead(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    date_created: datetime
    date_updated: datetime