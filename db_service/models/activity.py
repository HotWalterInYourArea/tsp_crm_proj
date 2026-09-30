from absctract_models.base_model import BaseModel
from deal import Deal
from sqlalchemy import(
String, ForeignKey, Text)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID as uuid
from sqlalchemy.sql import func

class Activity_Type(BaseModel):
    __tablename__ = 'activity_type'
    name = Mapped[str] = mapped_column(String(100), unique = True, nullable = False, default = "Новый тип дела")
    activities: Mapped[list["Activity"]] = relationship(back_populates = 'activity_type')
    
class Activity(BaseModel):
    __tablename__ = 'activity'
    description: Mapped[str] = mapped_column(Text, nullable = True)
    activity_type_name: Mapped[str] = mapped_column(String(100), ForeignKey('activity_type.name'), nullable = True)
    activity_type: Mapped["Activity_Type"] = relationship(back_populates = 'activities')
    deal_id: Mapped[uuid] = mapped_column(PgUUID, ForeignKey('deal.id'), nullable = False)
    deal: Mapped["Deal"] = relationship(back_populates = 'activities')