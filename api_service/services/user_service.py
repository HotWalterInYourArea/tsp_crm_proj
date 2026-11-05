import uuid
from sqlalchemy.orm import Session

from api_service.core.security import hash_password
from db_service.models.user import User
from db_service.repositories.user_repository import UserRepository, UserRoleRepository
from db_service.repositories.department_repository import DepartmentRepository
from api_service.schemas.user_schema import (
    UserCreate, UserUpdate, UserRead,
    UserRoleCreate, UserRoleUpdate, UserRoleRead,
)


import uuid
from sqlalchemy.orm import Session

from db_service.repositories.user_repository import UserRoleRepository
from api_service.schemas.user_schema import UserRoleCreate, UserRoleUpdate, UserRoleRead
from api_service.services._cached import (
    get_cached_item, set_cached_item,
    get_cached_list, set_cached_list,
    invalidate_item, invalidate_all,
)


class UserRoleService:
    PREFIX = "roles"

    def __init__(self, session: Session):
        self.session = session
        self.repo = UserRoleRepository(session)

    def get(self, role_id: uuid.UUID) -> UserRoleRead:
        cached = get_cached_item(self.PREFIX, role_id, UserRoleRead.model_validate)
        if cached is not None:
            return cached

        orm = self.repo.get(role_id)
        if orm is None:
            raise ValueError(f"UserRole {role_id} not found")
        dto = UserRoleRead.model_validate(orm)
        set_cached_item(self.PREFIX, role_id, dto.model_dump(mode="json"))
        return dto

    def list(self, **kw) -> list[UserRoleRead]:
        cached = get_cached_list(self.PREFIX, kw, UserRoleRead.model_validate)
        if cached is not None:
            return cached

        orms = self.repo.list(**kw)
        dtos = [UserRoleRead.model_validate(o) for o in orms]
        set_cached_list(self.PREFIX, kw, [d.model_dump(mode="json") for d in dtos])
        return dtos

    def create(self, payload: UserRoleCreate) -> UserRoleRead:
        if self.repo.get_by_name(payload.name):
            raise ValueError(f"Role {payload.name!r} already exists")
        orm = self.repo.add(self.repo.model(**payload.model_dump()))
        self.session.commit()
        self.session.refresh(orm)
        invalidate_all(self.PREFIX)
        return UserRoleRead.model_validate(orm)

    def update(self, role_id: uuid.UUID, payload: UserRoleUpdate) -> UserRoleRead:
        orm = self.repo.get(role_id)
        if orm is None:
            raise ValueError(f"UserRole {role_id} not found")
        data = payload.model_dump(exclude_unset=True)
        if "name" in data and data["name"] != orm.name and self.repo.get_by_name(data["name"]):
            raise ValueError("Role name already in use")
        for f, v in data.items():
            setattr(orm, f, v)
        self.session.commit()
        self.session.refresh(orm)
        invalidate_item(self.PREFIX, role_id)
        return UserRoleRead.model_validate(orm)

    def delete(self, role_id: uuid.UUID) -> None:
        orm = self.repo.get(role_id)
        if orm is None:
            raise ValueError(f"UserRole {role_id} not found")
        if orm.users:
            raise ValueError("Cannot delete role with users")
        self.repo.delete(orm)
        self.session.commit()
        invalidate_item(self.PREFIX, role_id)


class UserService:
    PREFIX = "users"

    def __init__(self, session: Session):
        self.session = session
        self.repo = UserRepository(session)
        self.role_repo = UserRoleRepository(session)
        self.dept_repo = DepartmentRepository(session)

    def get(self, user_id: uuid.UUID) -> UserRead:
        cached = get_cached_item(self.PREFIX, user_id, UserRead.model_validate)
        if cached is not None:
            return cached

        orm = self.repo.get(user_id)
        if orm is None:
            raise ValueError(f"User {user_id} not found")
        dto = UserRead.model_validate(orm)
        set_cached_item(self.PREFIX, user_id, dto.model_dump(mode="json"))
        return dto

    def list(self, **kw) -> list[UserRead]:
        cached = get_cached_list(self.PREFIX, kw, UserRead.model_validate)
        if cached is not None:
            return cached

        orms = self.repo.list(**kw)
        dtos = [UserRead.model_validate(o) for o in orms]
        set_cached_list(self.PREFIX, kw, [d.model_dump(mode="json") for d in dtos])
        return dtos

    def create_user_by_admin(self, payload: UserCreate) -> UserRead:
        orm = self._create_user_impl(payload)
        invalidate_all(self.PREFIX)
        invalidate_all("departments")
        return UserRead.model_validate(orm)

    def create_user_by_head(self, payload: UserCreate, current_head: User) -> UserRead:
        supervised_dept_ids = {d.id for d in current_head.supervised_departments}
        if payload.department_id not in supervised_dept_ids:
            raise PermissionError("You can only create users in departments you supervise")
        orm = self._create_user_impl(payload)
        invalidate_all(self.PREFIX)
        invalidate_all("departments")
        return UserRead.model_validate(orm)

    def _create_user_impl(self, payload: UserCreate) -> User:
        if self.repo.get_by_email(payload.email):
            raise ValueError("Email already in use")
        if self.repo.get_by_login(payload.login):
            raise ValueError("Login already in use")
        if self.role_repo.get(payload.role_id) is None:
            raise ValueError("Role not found")
        if payload.department_id and self.dept_repo.get(payload.department_id) is None:
            raise ValueError("Department not found")
        orm = self.repo.add(
            self.repo.model(
                name=payload.name,
                email=payload.email,
                phone=payload.phone,
                login=payload.login,
                hashed_password=hash_password(payload.password),
                role_id=payload.role_id,
                department_id=payload.department_id,
            )
        )
        self.session.commit()
        self.session.refresh(orm)
        return orm

    def update_user_by_admin(self, user_id: uuid.UUID, payload: UserUpdate) -> UserRead:
        orm = self.repo.get(user_id)
        if orm is None:
            raise ValueError(f"User {user_id} not found")
        dto = self._update_user_impl(orm, payload)
        invalidate_item(self.PREFIX, user_id)
        invalidate_all("departments")
        return dto

    def update_user_by_head(self, user_id: uuid.UUID, payload: UserUpdate, current_head: User) -> UserRead:
        orm = self.repo.get(user_id)
        if orm is None:
            raise ValueError(f"User {user_id} not found")

        supervised_dept_ids = {d.id for d in current_head.supervised_departments}
        if orm.department_id not in supervised_dept_ids:
            raise PermissionError("You can only edit users in departments you supervise")
        if payload.department_id is not None and payload.department_id != orm.department_id:
            raise PermissionError("You cannot change the user's department")

        dto = self._update_user_impl(orm, payload)
        invalidate_item(self.PREFIX, user_id)
        return dto

    def _update_user_impl(self, orm: User, payload: UserUpdate) -> UserRead:
        data = payload.model_dump(exclude_unset=True)
        if "password" in data:
            orm.hashed_password = hash_password(data.pop("password"))
        if "email" in data and data["email"] != orm.email and self.repo.get_by_email(data["email"]):
            raise ValueError("Email already in use")
        if "role_id" in data and self.role_repo.get(data["role_id"]) is None:
            raise ValueError("Role not found")
        if "department_id" in data and data["department_id"] and self.dept_repo.get(data["department_id"]) is None:
            raise ValueError("Department not found")
        for f, v in data.items():
            setattr(orm, f, v)
        self.session.commit()
        self.session.refresh(orm)
        return UserRead.model_validate(orm)

    def delete_user_by_admin(self, user_id: uuid.UUID) -> None:
        orm = self.repo.get(user_id)
        if orm is None:
            raise ValueError(f"User {user_id} not found")
        self.repo.delete(orm)
        self.session.commit()
        invalidate_item(self.PREFIX, user_id)
        invalidate_all("departments")

    def delete_user_by_head(self, user_id: uuid.UUID, current_head: User) -> None:
        orm = self.repo.get(user_id)
        if orm is None:
            raise ValueError(f"User {user_id} not found")
        supervised_dept_ids = {d.id for d in current_head.supervised_departments}
        if orm.department_id not in supervised_dept_ids:
            raise PermissionError("You can only delete users in departments you supervise")
        if orm.id == current_head.id:
            raise ValueError("You cannot delete yourself")
        self.repo.delete(orm)
        self.session.commit()
        invalidate_item(self.PREFIX, user_id)
        invalidate_all("departments")


    def update_self(self, current_user: User, payload: UserUpdate) -> UserRead:
        orm = self.repo.get(current_user.id)
        if orm is None:
            raise ValueError(f"User {current_user.id} not found")

        if payload.role_id is not None:
            raise PermissionError("You cannot change your own role")
        if payload.department_id is not None:
            raise PermissionError("You cannot change your own department")

        data = payload.model_dump(exclude_unset=True)
        
        if "password" in data:
            orm.hashed_password = hash_password(data.pop("password"))
            
        if "email" in data and data["email"] != orm.email:
            if self.repo.get_by_email(data["email"]):
                raise ValueError("Email already in use")

        for f, v in data.items():
            setattr(orm, f, v)
            
        self.session.commit()
        self.session.refresh(orm)
        
        invalidate_item(self.PREFIX, current_user.id)
        return UserRead.model_validate(orm)
        