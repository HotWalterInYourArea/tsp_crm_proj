from db_service.models.abstract_models import Item
from db_service.models.abstract_models import Person
from sqlalchemy import(
String, ForeignKey)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID as uuid

class UserRole(Item):
    __tablename__ = "user_role"
    default_name: str = "Новая роль"
    name_unique: bool = True
    users: Mapped[list["User"]] = relationship(back_populates = "user_role")

class User(Person):
    __tablename__ = "user"
    default_name: str = "Новый пользователь"
    allowed_order_by: list[str] = ["name", "created_at", "updated_at", "login"]
    login: Mapped[str] = mapped_column(String(100), nullable = False, unique = True, index = True)
    hashed_password: Mapped[str] = mapped_column(String(100), nullable = False)
    assigned_deals: Mapped[list["Deal"]] = relationship("Deal", back_populates = "assigned_by", foreign_keys = "Deal.assigned_by_id")
    supervised_deals: Mapped[list["Deal"]] = relationship("Deal", back_populates = "supervised_by", secondary = "supervisor_user_deal")
    created_deals: Mapped[list["Deal"]] = relationship("Deal", back_populates = "created_by", foreign_keys = "Deal.created_by_id")
    clients: Mapped[list["Client"]] = relationship("Client", back_populates = "responsible_user")
    activities: Mapped[list["Activity"]] = relationship("Activity", back_populates = "user")
    user_role: Mapped["UserRole"] = relationship(back_populates = "users")
    role_id: Mapped[uuid] = mapped_column(PgUUID, ForeignKey("user_role.id"), nullable = False)
    department_id: Mapped[uuid | None]  = mapped_column(PgUUID, ForeignKey("department.id"), nullable = True)
    department: Mapped["Department"] = relationship("Department", back_populates = "users", foreign_keys=[department_id])
    supervised_department: Mapped["Department"] = relationship("Department", back_populates = "head_user", foreign_keys = "Department.head_user_id")


    