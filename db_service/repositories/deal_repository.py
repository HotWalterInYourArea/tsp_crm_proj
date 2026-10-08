import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

from db_service.models.deal import Deal
from db_service.repositories.item_repository import ItemRepository


class DealRepository(ItemRepository[Deal]):
    model = Deal

    def get(self, deal_id: uuid.UUID) -> Deal | None:
        stmt = (
            select(Deal)
            .where(Deal.id == deal_id)
            .options(
                selectinload(Deal.contact_clients),
                selectinload(Deal.supervised_by),
                joinedload(Deal.activities)
            )
        )
        return self.session.execute(stmt).unique().scalar_one_or_none()
    
    def get_without_activities(self, deal_id: uuid.UUID) -> Deal | None:
        stmt = (
            select(Deal)
            .where(Deal.id == deal_id)
            .options(
                selectinload(Deal.contact_clients),
                selectinload(Deal.supervised_by)
            )
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_pipeline(self, pipeline_id: uuid.UUID) -> list[Deal]:
        stmt = select(Deal).where(Deal.pipeline_id == pipeline_id)
        return list(self.session.execute(stmt).scalars().all())

    def list_by_stage(self, pipeline_stage_id: uuid.UUID) -> list[Deal]:
        stmt = select(Deal).where(Deal.pipeline_stage_id == pipeline_stage_id)
        return list(self.session.execute(stmt).scalars().all())

    def list_by_client(self, client_id: uuid.UUID) -> list[Deal]:
        stmt = select(Deal).where(Deal.main_client_id == client_id)
        return list(self.session.execute(stmt).scalars().all())

    def list_by_assigned_user(self, user_id: uuid.UUID) -> list[Deal]:
        stmt = select(Deal).where(Deal.assigned_by_id == user_id)
        return list(self.session.execute(stmt).scalars().all())

    def list_by_budget_range(self, min_budget: int, max_budget: int) -> list[Deal]:
        stmt = (
            select(Deal)
            .where(Deal.budget.is_not(None))
            .where(Deal.budget >= min_budget)
            .where(Deal.budget <= max_budget)
        )
        return list(self.session.execute(stmt).scalars().all())


    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        pipeline_id: uuid.UUID | None = None,
        pipeline_stage_id: uuid.UUID | None = None,
        assigned_by_id: uuid.UUID | None = None,
        main_client_id: uuid.UUID | None = None,
        name_contains: str | None = None,
        min_budget: int | None = None,
        max_budget: int | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        updated_from: datetime | None = None,
        updated_to: datetime | None = None,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> list[Deal]:
        stmt = select(Deal).options(
            selectinload(Deal.contact_clients),
            selectinload(Deal.supervised_by),
        )
        if pipeline_id:
            stmt = stmt.where(Deal.pipeline_id == pipeline_id)
        if pipeline_stage_id:
            stmt = stmt.where(Deal.pipeline_stage_id == pipeline_stage_id)
        if assigned_by_id:
            stmt = stmt.where(Deal.assigned_by_id == assigned_by_id)
        if main_client_id:
            stmt = stmt.where(Deal.main_client_id == main_client_id)
        if name_contains:
            stmt = stmt.where(Deal.name.ilike(f"%{name_contains}%"))
        if min_budget is not None:
            stmt = stmt.where(Deal.budget >= min_budget)
        if max_budget is not None:
            stmt = stmt.where(Deal.budget <= max_budget)

        stmt = self._apply_date_filters(
            stmt,
            created_from=created_from, created_to=created_to,
            updated_from=updated_from, updated_to=updated_to,
        )
        stmt = self._apply_ordering(stmt, order_by=order_by, order_desc=order_desc)
        return list(self.session.execute(stmt.offset(offset).limit(limit)).scalars().all())

    def count(
        self,
        *,
        pipeline_id: uuid.UUID | None = None,
        pipeline_stage_id: uuid.UUID | None = None,
        assigned_by_id: uuid.UUID | None = None,
        main_client_id: uuid.UUID | None = None,
        min_budget: int | None = None,
        max_budget: int | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        updated_from: datetime | None = None,
        updated_to: datetime | None = None,
    ) -> int:
        from sqlalchemy import func

        stmt = select(func.count()).select_from(Deal)
        if pipeline_id:
            stmt = stmt.where(Deal.pipeline_id == pipeline_id)
        if pipeline_stage_id:
            stmt = stmt.where(Deal.pipeline_stage_id == pipeline_stage_id)
        if assigned_by_id:
            stmt = stmt.where(Deal.assigned_by_id == assigned_by_id)
        if main_client_id:
            stmt = stmt.where(Deal.main_client_id == main_client_id)
        if min_budget is not None:
            stmt = stmt.where(Deal.budget >= min_budget)
        if max_budget is not None:
            stmt = stmt.where(Deal.budget <= max_budget)
        stmt = self._apply_date_filters(
            stmt,
            created_from=created_from, created_to=created_to,
            updated_from=updated_from, updated_to=updated_to,
        )
        return self.session.execute(stmt).scalar_one()

    def total_budget(
        self,
        *,
        pipeline_id: uuid.UUID | None = None,
        assigned_by_id: uuid.UUID | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> int:
        from sqlalchemy import func

        stmt = select(func.coalesce(func.sum(Deal.budget), 0)).select_from(Deal)
        if pipeline_id:
            stmt = stmt.where(Deal.pipeline_id == pipeline_id)
        if assigned_by_id:
            stmt = stmt.where(Deal.assigned_by_id == assigned_by_id)
        stmt = self._apply_date_filters(
            stmt,
            created_from=created_from, created_to=created_to,
            updated_from=None, updated_to=None,
        )
        return int(self.session.execute(stmt).scalar_one())