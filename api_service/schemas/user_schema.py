import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from api_service.core.validators import normalize_phone, is_valid_phone

class UserRoleBase(BaseModel):
    name: str = Field(default="Новая роль", max_length=100)

class UserRoleCreate(UserRoleBase):
    pass

class UserRoleUpdate(BaseModel):
    name: str | None = None

class UserRoleRead(UserRoleBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class UserBase(BaseModel):
    name: str = Field(max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=16)
    login: str = Field(max_length=100)
    role_id: uuid.UUID
    department_id: uuid.UUID | None = None
    @field_validator("phone", mode="before")
    @classmethod
    def _normalize_and_validate_phone(cls, v):
        if v is None or v == "":
            return None
        normalized = normalize_phone(v)
        if not is_valid_phone(normalized):
            raise ValueError("Phone must contain only digits with an optional leading '+'")
        return normalized


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    password: str | None = Field(default=None, min_length=6)
    role_id: uuid.UUID | None = None
    department_id: uuid.UUID | None = None
    @field_validator("phone", mode="before")
    @classmethod
    def _normalize_and_validate_phone(cls, v):
        if v is None or v == "":
            return None
        normalized = normalize_phone(v)
        if not is_valid_phone(normalized):
            raise ValueError("Phone must contain only digits with an optional leading '+'")
        return normalized


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime