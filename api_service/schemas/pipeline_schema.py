import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PipelineBase(BaseModel):
    name: str = Field(default="Новая воронка", max_length=100)

class PipelineCreate(PipelineBase):
    pass

class PipelineUpdate(BaseModel):
    name: str | None = None

class PipelineRead(PipelineBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    date_created: datetime
    date_updated: datetime


class PipelineStageBase(BaseModel):
    name: str = Field(default="Новая стадия", max_length=100)
    pipeline_id: uuid.UUID

class PipelineStageCreate(PipelineStageBase):
    pass

class PipelineStageUpdate(BaseModel):
    name: str | None = None
    pipeline_id: uuid.UUID | None = None
    
class PipelineStageRead(PipelineStageBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    date_created: datetime
    date_updated: datetime