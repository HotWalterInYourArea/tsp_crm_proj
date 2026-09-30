from absctract_models.base_model import BaseModel
from activity import Activity
from sqlalchemy import(
String, Integer, list)
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Deal(BaseModel):
    __tablename__ = 'deal'
    name: Mapped[str] = mapped_column(String(100), nullable = False, default = "Новая сделка")
    budget: Mapped[int] = mapped_column(Integer, nullable = True)
    activities: Mapped[list["Activity"]] = relationship('Activity', back_populates = 'deal_id', cascade = 'all,delete' )