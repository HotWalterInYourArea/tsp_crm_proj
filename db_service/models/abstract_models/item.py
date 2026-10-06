from db_service.declarative_base import Base
from sqlalchemy import(DateTime, true)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from uuid import uuid7, UUID as uuid


class Item(Base):
    __abstract__ = True
    id: Mapped[uuid] = mapped_column(PgUUID, primary_key = True, default=uuid7)
    date_created: Mapped[DateTime] = mapped_column(DateTime(timezone = true), nullable = False, server_default = func.now())
    date_updated: Mapped[DateTime] = mapped_column(
                                                    DateTime(timezone = true), nullable = False, server_default = func.now(),
                                                    onupdate = func.now()
                                                )