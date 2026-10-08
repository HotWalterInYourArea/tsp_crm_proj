import uuid
from datetime import datetime
from typing import Generic, TypeVar, Type, Any

from sqlalchemy import select, func, Select
from sqlalchemy.orm import Session

from db_service.models.abstract_models.item import Item

ModelT = TypeVar("ModelT", bound = Item)


class ItemRepository(Generic[ModelT]):
    model: Type[ModelT]

    def __init__(self, session: Session):
        self.session = session

    def get(self, entity_id: uuid.UUID) -> ModelT | None:
        return self.session.get(self.model, entity_id)

    def exists(self, entity_id: uuid.UUID) -> bool:
        stmt = select(self.model.id).where(self.model.id == entity_id).limit(1)
        return self.session.execute(stmt).scalar_one_or_none() is not None

    def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        self.session.flush()
        return entity

    def delete(self, entity: ModelT) -> None:
        self.session.delete(entity)
        self.session.flush()


    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        updated_from: datetime | None = None,
        updated_to: datetime | None = None,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> list[ModelT]:
        stmt = self._apply_date_filters(
            select(self.model),
            created_from = created_from,
            created_to = created_to,
            updated_from = updated_from,
            updated_to = updated_to,
        )
        stmt = self._apply_ordering(stmt, order_by=order_by, order_desc=order_desc)
        stmt = stmt.offset(offset).limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def count(
        self,
        *,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        updated_from: datetime | None = None,
        updated_to: datetime | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(self.model)
        stmt = self._apply_date_filters(
            stmt,
            created_from=created_from,
            created_to=created_to,
            updated_from=updated_from,
            updated_to=updated_to,
        )
        return self.session.execute(stmt).scalar_one()


    def _apply_date_filters(
        self,
        stmt: Select,
        *,
        created_from: datetime | None,
        created_to: datetime | None,
        updated_from: datetime | None,
        updated_to: datetime | None,
    ) -> Select:
        if created_from is not None:
            stmt = stmt.where(self.model.created_at >= created_from)
        if created_to is not None:
            stmt = stmt.where(self.model.created_at <= created_to)
        if updated_from is not None:
            stmt = stmt.where(self.model.updated_at >= updated_from)
        if updated_to is not None:
            stmt = stmt.where(self.model.updated_at <= updated_to)
        return stmt

    def _apply_ordering(self, stmt: Select, *, order_by: str, order_desc: bool) -> Select:
        column = getattr(self.model, order_by, None)
        if order_by not in self.model.allowed_order_by:
            order_by = "created_at"
        if column is None:
            column = self.model.created_at
        return stmt.order_by(column.desc() if order_desc else column.asc())