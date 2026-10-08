import uuid
from datetime import datetime

from sqlalchemy import select

from db_service.models.department import Department
from db_service.repositories.item_repository import ItemRepository


class DepartmentRepository(ItemRepository[Department]):
    model = Department

    def get_by_name(self, name: str) -> Department | None:
        stmt = select(Department).where(Department.name == name)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_head(self, head_user_id: uuid.UUID) -> list[Department]:
        stmt = select(Department).where(Department.head_user_id == head_user_id)
        return list(self.session.execute(stmt).scalars().all())

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        head_user_id: uuid.UUID | None = None,
        name_contains: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        updated_from: datetime | None = None,
        updated_to: datetime | None = None,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> list[Department]:
        stmt = select(Department)
        if head_user_id:
            stmt = stmt.where(Department.head_user_id == head_user_id)
        if name_contains:
            stmt = stmt.where(Department.name.ilike(f"%{name_contains}%"))
        stmt = self._apply_date_filters(
            stmt,
            created_from=created_from, created_to=created_to,
            updated_from=updated_from, updated_to=updated_to,
        )
        stmt = self._apply_ordering(stmt, order_by=order_by, order_desc=order_desc)
        return list(self.session.execute(stmt.offset(offset).limit(limit)).scalars().all())