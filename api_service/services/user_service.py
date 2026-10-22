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


class UserRoleService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = UserRoleRepository(session)

    def get(self, role_id: uuid.UUID) -> UserRoleRead:
        orm = self.repo.get(role_id)
        if orm is None:
            raise ValueError(f"UserRole {role_id} not found")
        return UserRoleRead.model_validate(orm)

    def list(self, **kw) -> list[UserRoleRead]:
        return [UserRoleRead.model_validate(o) for o in self.repo.list(**kw)]

    def create(self, payload: UserRoleCreate) -> UserRoleRead:
        if self.repo.get_by_name(payload.name):
            raise ValueError(f"Role {payload.name!r} already exists")
        orm = self.repo.add(self.repo.model(**payload.model_dump()))
        self.session.commit()
        self.session.refresh(orm)
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
        return UserRoleRead.model_validate(orm)

    def delete(self, role_id: uuid.UUID) -> None:
        orm = self.repo.get(role_id)
        if orm is None:
            raise ValueError(f"UserRole {role_id} not found")
        if orm.users:
            raise ValueError("Cannot delete role with users")
        self.repo.delete(orm)
        self.session.commit()


class UserService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = UserRepository(session)
        self.role_repo = UserRoleRepository(session)
        self.dept_repo = DepartmentRepository(session) 

    def get(self, user_id: uuid.UUID) -> UserRead:
        orm = self.repo.get(user_id)
        if orm is None:
            raise ValueError(f"User {user_id} not found")
        return UserRead.model_validate(orm)

    def list(self, **kw) -> list[UserRead]:
        return [UserRead.model_validate(o) for o in self.repo.list(**kw)]

    def create_user_by_head(
        self,
        payload: UserCreate,
        current_head: User,
    ) -> UserRead:

        supervised_dept_ids = {d.id for d in current_head.supervised_departments}
        if payload.department_id not in supervised_dept_ids:
            raise PermissionError(
                "You can only create users in departments you supervise"
            )

        return self._create_user(payload)

    def create(self, payload: UserCreate) -> UserRead:
        if self.repo.get_by_email(payload.email):
            raise ValueError("Email already in use")
        if self.repo.get_by_login(payload.login):
            raise ValueError("Login already in use")
        if self.role_repo.get(payload.role_id) is None:
            raise ValueError("Role not found")

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
        return UserRead.model_validate(orm)

    def update(self, user_id: uuid.UUID, payload: UserUpdate) -> UserRead:
        orm = self.repo.get(user_id)
        if orm is None:
            raise ValueError(f"User {user_id} not found")
        data = payload.model_dump(exclude_unset=True)
        if "password" in data:
            orm.hashed_password = hash_password(data.pop("password"))
        if "email" in data and data["email"] != orm.email and self.repo.get_by_email(data["email"]):
            raise ValueError("Email already in use")
        if "role_id" in data and self.role_repo.get(data["role_id"]) is None:
            raise ValueError("Role not found")
        for f, v in data.items():
            setattr(orm, f, v)
        self.session.commit()
        self.session.refresh(orm)
        return UserRead.model_validate(orm)

    def delete(self, user_id: uuid.UUID) -> None:
        orm = self.repo.get(user_id)
        if orm is None:
            raise ValueError(f"User {user_id} not found")
        self.repo.delete(orm)
        self.session.commit()

    def delete_user_by_head(self, target_user_id: uuid.UUID, current_head: User) -> None:
        target_user = self.repo.get(target_user_id)
        if not target_user:
            raise ValueError("User not found")

        if target_user.department_id not in [d.id for d in current_head.supervised_departments]:
            raise PermissionError("You can only delete users from departments you supervise")

        if target_user.id == current_head.id:
            raise ValueError("You cannot delete yourself")

        self.repo.delete(target_user)
        self.session.commit()