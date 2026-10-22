import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class DealBase(BaseModel):
    name: str = Field(default="Новая сделка", max_length=100)
    main_client_id: uuid.UUID
    assigned_by_id: uuid.UUID
    created_by_id: uuid.UUID
    pipeline_id: uuid.UUID
    pipeline_stage_id: uuid.UUID
    budget: int | None = None


class DealCreate(DealBase):
    contact_client_ids: list[uuid.UUID] = Field(default_factory=list)
    supervisor_ids: list[uuid.UUID] = Field(default_factory=list)


class DealUpdate(BaseModel):
    name: str | None = None
    main_client_id: uuid.UUID | None = None
    assigned_by_id: uuid.UUID | None = None
    pipeline_id: uuid.UUID | None = None
    pipeline_stage_id: uuid.UUID | None = None
    budget: int | None = None
    contact_client_ids: list[uuid.UUID] | None = None
    supervisor_ids: list[uuid.UUID] | None = None


class DealRead(DealBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    date_created: datetime
    date_updated: datetime