import uuid
from datetime import datetime

from sqlalchemy import select

from db_service.models.pipeline import Pipeline, PipelineStage
from db_service.repositories.item_repository import ItemRepository


class PipelineRepository(ItemRepository[Pipeline]):
    model = Pipeline

    def get_by_name(self, name: str) -> Pipeline | None:
        stmt = select(Pipeline).where(Pipeline.name == name)
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
    ) -> list[Pipeline]:
        stmt = select(Pipeline)
        if name_contains:
            stmt = stmt.where(Pipeline.name.ilike(f"%{name_contains}%"))
        stmt = self._apply_date_filters(
            stmt,
            created_from=created_from, created_to=created_to,
            updated_from=updated_from, updated_to=updated_to,
        )
        stmt = self._apply_ordering(stmt, order_by=order_by, order_desc=order_desc)
        return list(self.session.execute(stmt.offset(offset).limit(limit)).scalars().all())


class PipelineStageRepository(ItemRepository[PipelineStage]):
    model = PipelineStage

    def list_by_pipeline(self, pipeline_id: uuid.UUID) -> list[PipelineStage]:
        stmt = (
            select(PipelineStage)
            .where(PipelineStage.pipeline_id == pipeline_id)
            .order_by(PipelineStage.created_at.asc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        pipeline_id: uuid.UUID | None = None,
        name_contains: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        updated_from: datetime | None = None,
        updated_to: datetime | None = None,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> list[PipelineStage]:
        stmt = select(PipelineStage)
        if pipeline_id:
            stmt = stmt.where(PipelineStage.pipeline_id == pipeline_id)
        if name_contains:
            stmt = stmt.where(PipelineStage.name.ilike(f"%{name_contains}%"))
        stmt = self._apply_date_filters(
            stmt,
            created_from=created_from, created_to=created_to,
            updated_from=updated_from, updated_to=updated_to,
        )
        stmt = self._apply_ordering(stmt, order_by=order_by, order_desc=order_desc)
        return list(self.session.execute(stmt.offset(offset).limit(limit)).scalars().all())