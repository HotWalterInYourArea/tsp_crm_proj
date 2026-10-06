from db_service.models.abstract_models.item import Item
from sqlalchemy import(
String, ForeignKey)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID as uuid

class Pipeline(Item):
    __tablename__ = 'pipeline'
    name: Mapped[str] = mapped_column(String(100), nullable = False, default = "Новая воронка", unique = True)
    pipeline_stages: Mapped[list["PipelineStage"]] = relationship("PipelineStage", back_populates = "pipeline_stage")
