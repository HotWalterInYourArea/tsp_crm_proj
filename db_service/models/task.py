from absctract_models.base_model import BaseModel
from activity import Activity
from sqlalchemy import(
DateTime, true)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import uuid4, UUID as uuid
from sqlalchemy.sql import func
class Task(BaseModel):
    __tablename__ = 'task'