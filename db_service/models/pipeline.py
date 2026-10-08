from db_service.models.abstract_models import Item
from sqlalchemy import(
String, ForeignKey)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID as uuid

class Pipeline(Item):
    __tablename__ = "pipeline"
    default_name: str = "Новая воронка"
    name_unique: bool = True
    pipeline_stages: Mapped[list["PipelineStage"]] = relationship("PipelineStage", back_populates = "pipeline")
    deals: Mapped[list["Deal"]] = relationship("Deal", back_populates = "pipeline")

class PipelineStage(Item):
    __tablename__ = "pipeline_stage"
    default_name: str = "Новая стадия"
    pipeline_id: Mapped[uuid] = mapped_column(PgUUID, ForeignKey("pipeline.id"), nullable = False)
    pipeline: Mapped["Pipeline"] = relationship("Pipeline", back_populates = "pipeline_stages")
    deals: Mapped[list["Deal"]] = relationship("Deal", back_populates = "pipeline_stage")