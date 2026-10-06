from db_service.models.abstract_models.item import Item
from sqlalchemy import(
String, ForeignKey)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID as uuid

class PipelineStage(Item):
    __tablename__ = 'pipeline_stage'
    name: Mapped[str] = mapped_column(String(100), nullable = False, default = "Новая стадия", unique = True)
    pipeline_id: Mapped[uuid] = mapped_column(PgUUID, ForeignKey('pipeline.id'), nullable = False)
    pipeline: Mapped["Pipeline"] = relationship("Pipeline", back_populates = "pipeline_stages")
    deals: Mapped[list["Deal"]] = relationship("Deal", back_populates = "pipeline_stage")