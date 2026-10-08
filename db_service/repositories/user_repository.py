import uuid
from datetime import datetime

from sqlalchemy import select

from db_service.models.user import User, UserRole
from db_service.repositories.item_repository import ItemRepository


class UserRoleRepository(ItemRepository[UserRole]):
    model = UserRole

    def get_by_name(self, name: str) -> UserRole | None:
        stmt = select(UserRole).where(UserRole.name == name)
        return self.session.execute(stmt).scalar_one_or_none()

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        name_contains: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        updated_from: datetime | None = None,
        updated_to: datetime | None = None,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> list[UserRole]:
        stmt = select(UserRole)
        if name_contains:
            stmt = stmt.where(UserRole.name.ilike(f"%{name_contains}%"))
        stmt = self._apply_date_filters(
            stmt,
            created_from=created_from, created_to=created_to,
            updated_from=updated_from, updated_to=updated_to,
        )
        stmt = self._apply_ordering(stmt, order_by=order_by, order_desc=order_desc)
        return list(self.session.execute(stmt.offset(offset).limit(limit)).scalars().all())


class UserRepository(ItemRepository[User]):
    model = User

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_login(self, login: str) -> User | None:
        stmt = select(User).where(User.login == login)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_department(self, department_id: uuid.UUID) -> list[User]:
        stmt = select(User).where(User.department_id == department_id)
        return list(self.session.execute(stmt).scalars().all())

    def list_by_role(self, role_id: uuid.UUID) -> list[User]:
        stmt = select(User).where(User.role_id == role_id)
        return list(self.session.execute(stmt).scalars().all())

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        role_id: uuid.UUID | None = None,
        department_id: uuid.UUID | None = None,
        name_contains: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        updated_from: datetime | None = None,
        updated_to: datetime | None = None,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> list[User]:
        stmt = select(User)
        if role_id:
            stmt = stmt.where(User.role_id == role_id)
        if department_id:
            stmt = stmt.where(User.department_id == department_id)
        if name_contains:
            stmt = stmt.where(User.name.ilike(f"%{name_contains}%"))
        stmt = self._apply_date_filters(
            stmt,
            created_from=created_from, created_to=created_to,
            updated_from=updated_from, updated_to=updated_to,
        )
        stmt = self._apply_ordering(stmt, order_by=order_by, order_desc=order_desc)
        return list(self.session.execute(stmt.offset(offset).limit(limit)).scalars().all())