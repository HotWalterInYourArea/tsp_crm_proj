from db_service.models.abstract_models.item import Item
from sqlalchemy import(
String, ForeignKey)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID as uuid

class Department(Item):
    __tablename__ = 'department'
    name: Mapped[str] = mapped_column(String(100), nullable = False, default = "Новый отдел")
    head_user_id: Mapped[uuid] = mapped_column(PgUUID, ForeignKey('user.id'), nullable = True)
    head_user: Mapped["User"] = relationship("User", back_populates = "supervised_department")
    users: Mapped[list["User"]] = relationship("User", back_populates = "department")
