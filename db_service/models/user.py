from absctract_models.base_model import BaseModel
from deal import Deal
from client import Client
from sqlalchemy import(
String,
DateTime, true)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

class User(BaseModel):
    __tablename__ = 'user'
    name: Mapped[str] = mapped_column(String(100), nullable = False, default = "Новый клиент")
    email:  Mapped[str] = mapped_column(String(100), nullable = False, unique = True)
    hash_password: Mapped[str] = mapped_column(String(100), nullable = False)
    
    deals: Mapped[list["Deal"]] = relationship(back_populates = "client")
    user: Mapped["Client"] = relationship(back_populates = "user")
    