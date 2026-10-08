from db_service.declarative_base import Base
from db_service.models.abstract_models.item import Item
from sqlalchemy import(String, CheckConstraint)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from uuid import uuid7, UUID as uuid


class Person(Item):
    __abstract__ = True
    email:  Mapped[str] = mapped_column(String(100), nullable = False, unique = True)
    phone:  Mapped[str] = mapped_column(String(16), nullable = True)
    __table_args__ = (
            CheckConstraint(
                "phone IS NULL OR phone ~ '^\\+?[0-9]+$'", 
                name="phone_digits_or_null"
            ),
            CheckConstraint(
                "email IS NULL OR email LIKE '%@%'", 
                name="email_at_or_null"
            ),
        )