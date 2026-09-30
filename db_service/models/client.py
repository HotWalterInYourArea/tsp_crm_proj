from absctract_models.base_model import BaseModel
from deal import Deal
from user import User
from activity import Activity
from sqlalchemy import(
String, CheckConstraint)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import uuid4, UUID as uuid
from sqlalchemy.sql import func

class Client(BaseModel):
    __tablename__ = 'client'
    name: Mapped[str] = mapped_column(String(100), nullable = False, default = "Новый клиент")
    email:  Mapped[str] = mapped_column(String(100), nullable = True)
    phone:  Mapped[str] = mapped_column(String(16), nullable = True)
    deals: Mapped[list["Deal"]] = relationship(back_populates = "client")
    user: Mapped["User"] = relationship(back_populates = "clients")
    __table_args__ = (
        CheckConstraint(
            "phone IS NULL OR phone ~ ''^\\+?[0-9]+$'", 
            name="phone_digits_or_null"
        ),
        CheckConstraint(
            "email IS NULL OR email LIKE '%@%'", 
            name="email_at_or_null"
        ),
    )