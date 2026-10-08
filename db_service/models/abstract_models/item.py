from db_service.declarative_base import Base
from sqlalchemy import(DateTime, true, String)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, declared_attr
from sqlalchemy.sql import func
from datetime import datetime
from uuid import uuid7, UUID as uuid


class Item(Base):
    __abstract__ = True
    default_name: str = "Новый объект"
    name_unique: bool = False
    allowed_order_by: list[str] = ["name", "created_at", "updated_at"]
    id: Mapped[uuid] = mapped_column(PgUUID, primary_key = True, default=uuid7)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone = true), nullable = False, server_default = func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone = true), nullable = False, server_default = func.now(),
                                                   onupdate = func.now())
    @declared_attr
    def name(cls) -> Mapped[str]:
        return mapped_column(String(100), server_default=cls.default_name, nullable = False, unique = cls.name_unique)