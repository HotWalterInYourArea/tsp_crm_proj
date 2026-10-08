import uuid
from datetime import datetime

from sqlalchemy import select

from db_service.models.activity import Activity, ActivityType
from db_service.repositories.item_repository import ItemRepository


class ActivityTypeRepository(ItemRepository[ActivityType]):
    model = ActivityType

    def get_by_name(self, name: str) -> ActivityType | None:
        stmt = select(ActivityType).where(ActivityType.name == name)
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
    ) -> list[ActivityType]:
        stmt = select(ActivityType)
        if name_contains:
            stmt = stmt.where(ActivityType.name.ilike(f"%{name_contains}%"))
        stmt = self._apply_date_filters(
            stmt,
            created_from=created_from, created_to=created_to,
            updated_from=updated_from, updated_to=updated_to,
        )
        stmt = self._apply_ordering(stmt, order_by=order_by, order_desc=order_desc)
        return list(self.session.execute(stmt.offset(offset).limit(limit)).scalars().all())


class ActivityRepository(ItemRepository[Activity]):
    model = Activity

    def list_by_deal(self, deal_id: uuid.UUID) -> list[Activity]:
        stmt = (
            select(Activity)
            .where(Activity.deal_id == deal_id)
            .order_by(Activity.created_at.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def list_by_user(self, user_id: uuid.UUID) -> list[Activity]:
        stmt = (
            select(Activity)
            .where(Activity.user_id == user_id)
            .order_by(Activity.created_at.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def list_by_type(self, activity_type_id: uuid.UUID) -> list[Activity]:
        stmt = (
            select(Activity)
            .where(Activity.activity_type_id == activity_type_id)
            .order_by(Activity.created_at.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def list_with_pending_deadline(self, before: datetime) -> list[Activity]:
        stmt = (
            select(Activity)
            .where(Activity.deadline_at.is_not(None))
            .where(Activity.deadline_at <= before)
            .order_by(Activity.deadline_at.asc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        deal_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        activity_type_id: uuid.UUID | None = None,
        has_deadline_at: bool | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        updated_from: datetime | None = None,
        updated_to: datetime | None = None,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> list[Activity]:
        stmt = select(Activity)
        if deal_id:
            stmt = stmt.where(Activity.deal_id == deal_id)
        if user_id:
            stmt = stmt.where(Activity.user_id == user_id)
        if activity_type_id:
            stmt = stmt.where(Activity.activity_type_id == activity_type_id)
        if has_deadline_at is True:
            stmt = stmt.where(Activity.deadline_at.is_not(None))
        elif has_deadline_at is False:
            stmt = stmt.where(Activity.deadline_at.is_(None))
        stmt = self._apply_date_filters(
            stmt,
            created_from=created_from, created_to=created_to,
            updated_from=updated_from, updated_to=updated_to,
        )
        stmt = self._apply_ordering(stmt, order_by=order_by, order_desc=order_desc)
        return list(self.session.execute(stmt.offset(offset).limit(limit)).scalars().all())