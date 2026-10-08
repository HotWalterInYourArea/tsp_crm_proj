from db_service.models.abstract_models import Item
from datetime import datetime
from sqlalchemy import(
String, Integer, ForeignKey, DateTime, true)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID as uuid
from sqlalchemy.dialects.postgresql import UUID as PgUUID

class Deal(Item):
    __tablename__ = "deal"
    default_name: str = "Новая сделка"
    allowed_order_by: list[str] = ["name", "created_at", "updated_at", "budget"]
    main_client: Mapped["Client"] = relationship("Client", back_populates = "deals")
    main_client_id: Mapped[uuid] = mapped_column(PgUUID, ForeignKey("client.id"), nullable = True)
    contact_clients: Mapped[list["Client"]] = relationship("Client", back_populates = "contact_deals", secondary = "contact_client_deal")
    assigned_by_id: Mapped[uuid] = mapped_column(PgUUID, ForeignKey("user.id"), nullable = True)
    created_by_id: Mapped[uuid] = mapped_column(PgUUID, ForeignKey("user.id"), nullable = False)
    assigned_by: Mapped["User"] = relationship("User", back_populates = "assigned_deals", foreign_keys = [assigned_by_id])
    created_by: Mapped["User"] = relationship("User", back_populates = "created_deals", foreign_keys = [created_by_id])
    supervised_by:  Mapped[list["User"]] = relationship("User", back_populates = "supervised_deals", secondary = "supervisor_user_deal")
    budget: Mapped[int|None] = mapped_column(Integer, nullable = True)
    activities: Mapped[list["Activity"]] = relationship("Activity", back_populates = "deal", cascade = "all,delete")
    pipeline_id: Mapped[uuid] = mapped_column(PgUUID, ForeignKey("pipeline.id"), nullable = False)
    pipeline_stage_id: Mapped[uuid] = mapped_column(PgUUID, ForeignKey("pipeline_stage.id"), nullable = False)
    pipeline: Mapped["Pipeline"] = relationship("Pipeline", back_populates = "deals")
    pipeline_stage: Mapped["PipelineStage"] = relationship("PipelineStage", back_populates = "deals")