from db_service.models.abstract_models.person import Person
from sqlalchemy import(
ForeignKey)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import uuid7, UUID as uuid
from sqlalchemy.sql import func

class Client(Person):
    __tablename__ = 'client'
    deals: Mapped[list["Deal"]] = relationship("Deal", back_populates = "main_client")
    contact_deals: Mapped[list["Deal"]] = relationship("Deal", back_populates = "contact_clients", secondary = 'contact_client_deal')
    responsible_user: Mapped["User"] = relationship("User", back_populates = "clients")
    responsible_user_id: Mapped[uuid] = mapped_column(PgUUID, ForeignKey('user.id'), nullable = False)