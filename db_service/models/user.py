from db_service.models.abstract_models.item import Item
from db_service.models.abstract_models.person import Person
from sqlalchemy import(
String, ForeignKey, CheckConstraint, true)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID as uuid

class UserRoles(Item):
    __tablename__ = 'user_role'
    name: Mapped[str] = mapped_column(String(100), nullable = False, unique = True, default = "Новая роль")
    users: Mapped[list["User"]] = relationship(back_populates = "user_role")

class User(Person):
    __tablename__ = 'user'
    login: Mapped[str] = mapped_column(String(100), nullable = False, unique = True)
    hashed_password: Mapped[str] = mapped_column(String(100), nullable = False)
    assigned_deals: Mapped[list["Deal"]] = relationship("Deal", back_populates = "assigned_by")
    supervised_deals: Mapped[list["Deal"]] = relationship("Deal", back_populates = "supervised_by", secondary = 'supervisor_user_deal')
    created_deals: Mapped[list["Deal"]] = relationship("Deal", back_populates = "created_by")
    clients: Mapped[list["Client"]] = relationship("Client", back_populates = "responsible_user")
    activities: Mapped[list["Activities"]] = relationship("Activity", back_populates = "user")
    role_name: Mapped[str] = mapped_column(String(100), ForeignKey('user_role.name'), nullable = False)
    role_id: Mapped[uuid] = mapped_column(PgUUID, ForeignKey('user_role.id'), nullable = False)
    department: Mapped["Department"] = relationship("Department", back_populates = "users")
    supervised_department: Mapped["Department"] = relationship("Department", back_populates = "head_user")
    supervised_department_id: Mapped[uuid] = mapped_column(PgUUID, ForeignKey('department.id'))
    department_id: Mapped[uuid]  = mapped_column(PgUUID, ForeignKey('department.id'))
    department_name: Mapped[str]  = mapped_column(String(100), ForeignKey('department.name'))


    