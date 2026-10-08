from db_service.models.abstract_models import Item
from sqlalchemy import(
String, ForeignKey)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID as uuid

class Department(Item):
    __tablename__ = "department"
    default_name: str = "Новый отдел"
    name_unique: bool = True
    head_user_id: Mapped[uuid] = mapped_column(PgUUID, ForeignKey("user.id", use_alter = True), nullable = True)
    head_user: Mapped["User"] = relationship("User", back_populates = "supervised_department", foreign_keys = [head_user_id])
    users: Mapped[list["User"]] = relationship("User", back_populates = "department", foreign_keys = "User.department_id")
