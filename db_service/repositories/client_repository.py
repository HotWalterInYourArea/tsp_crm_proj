import uuid
from datetime import datetime

from sqlalchemy import select

from db_service.models.client import Client
from db_service.repositories.item_repository import ItemRepository


class ClientRepository(ItemRepository[Client]):
    model = Client

    def get_by_email(self, email: str) -> Client | None:
        stmt = select(Client).where(Client.email == email)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_phone(self, phone: str) -> Client | None:
        stmt = select(Client).where(Client.phone == phone)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_responsible(self, user_id: uuid.UUID) -> list[Client]:
        stmt = select(Client).where(Client.responsible_user_id == user_id)
        return list(self.session.execute(stmt).scalars().all())

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        responsible_user_id: uuid.UUID | None = None,
        name_contains: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        updated_from: datetime | None = None,
        updated_to: datetime | None = None,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> list[Client]:
        stmt = select(Client)
        if responsible_user_id:
            stmt = stmt.where(Client.responsible_user_id == responsible_user_id)
        if name_contains:
            stmt = stmt.where(Client.name.ilike(f"%{name_contains}%"))
        stmt = self._apply_date_filters(
            stmt,
            created_from=created_from, created_to=created_to,
            updated_from=updated_from, updated_to=updated_to,
        )
        stmt = self._apply_ordering(stmt, order_by=order_by, order_desc=order_desc)
        return list(self.session.execute(stmt.offset(offset).limit(limit)).scalars().all())