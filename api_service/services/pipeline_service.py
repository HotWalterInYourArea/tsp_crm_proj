import uuid
from sqlalchemy.orm import Session

from db_service.repositories.pipeline_repository import PipelineRepository, PipelineStageRepository
from api_service.schemas.pipeline_schema import (
    PipelineCreate, PipelineUpdate, PipelineRead,
    PipelineStageCreate, PipelineStageUpdate, PipelineStageRead,
)
from api_service.services._cached import (
    get_cached_item, set_cached_item,
    get_cached_list, set_cached_list,
    invalidate_item, invalidate_all,
)

class PipelineService:
    PREFIX = "pipelines"

    def __init__(self, session: Session):
        self.session = session
        self.repo = PipelineRepository(session)

    def get(self, pid: uuid.UUID) -> PipelineRead:
        cached = get_cached_item(self.PREFIX, pid, PipelineRead.model_validate)
        if cached is not None:
            return cached

        orm = self.repo.get(pid)
        if orm is None:
            raise ValueError(f"Pipeline {pid} not found")
        dto = PipelineRead.model_validate(orm)
        set_cached_item(self.PREFIX, pid, dto.model_dump(mode="json"))
        return dto

    def list(self, **kw) -> list[PipelineRead]:
        cached = get_cached_list(self.PREFIX, kw, PipelineRead.model_validate)
        if cached is not None:
            return cached

        orms = self.repo.list(**kw)
        dtos = [PipelineRead.model_validate(o) for o in orms]
        set_cached_list(self.PREFIX, kw, [d.model_dump(mode="json") for d in dtos])
        return dtos

    def create(self, payload: PipelineCreate) -> PipelineRead:
        if self.repo.get_by_name(payload.name):
            raise ValueError(f"Pipeline {payload.name!r} already exists")
        orm = self.repo.add(self.repo.model(**payload.model_dump()))
        self.session.commit()
        self.session.refresh(orm)
        invalidate_all(self.PREFIX)
        return PipelineRead.model_validate(orm)

    def update(self, pid: uuid.UUID, payload: PipelineUpdate) -> PipelineRead:
        orm = self.repo.get(pid)
        if orm is None:
            raise ValueError(f"Pipeline {pid} not found")
        data = payload.model_dump(exclude_unset=True)
        if "name" in data and data["name"] != orm.name and self.repo.get_by_name(data["name"]):
            raise ValueError("Pipeline name already in use")
        for f, v in data.items():
            setattr(orm, f, v)
        self.session.commit()
        self.session.refresh(orm)
        invalidate_item(self.PREFIX, pid)
        return PipelineRead.model_validate(orm)

    def delete(self, pid: uuid.UUID) -> None:
        orm = self.repo.get(pid)
        if orm is None:
            raise ValueError(f"Pipeline {pid} not found")
        if orm.deals:
            raise ValueError("Cannot delete pipeline with deals")
        self.repo.delete(orm)
        self.session.commit()
        invalidate_item(self.PREFIX, pid)


class PipelineStageService:
    PREFIX = "pipeline_stages"

    def __init__(self, session: Session):
        self.session = session
        self.repo = PipelineStageRepository(session)
        self.pipe_repo = PipelineRepository(session)

    def get(self, sid: uuid.UUID) -> PipelineStageRead:
        cached = get_cached_item(self.PREFIX, sid, PipelineStageRead.model_validate)
        if cached is not None:
            return cached

        orm = self.repo.get(sid)
        if orm is None:
            raise ValueError(f"PipelineStage {sid} not found")
        dto = PipelineStageRead.model_validate(orm)
        set_cached_item(self.PREFIX, sid, dto.model_dump(mode="json"))
        return dto

    def list_by_pipeline(self, pid: uuid.UUID) -> list[PipelineStageRead]:
        cached = get_cached_list(self.PREFIX, {"pipeline_id": pid}, PipelineStageRead.model_validate)
        if cached is not None:
            return cached

        orms = self.repo.list_by_pipeline(pid)
        dtos = [PipelineStageRead.model_validate(o) for o in orms]
        set_cached_list(self.PREFIX, {"pipeline_id": pid}, [d.model_dump(mode="json") for d in dtos])
        return dtos

    def create(self, payload: PipelineStageCreate) -> PipelineStageRead:
        if self.pipe_repo.get(payload.pipeline_id) is None:
            raise ValueError("Pipeline not found")
        orm = self.repo.add(self.repo.model(**payload.model_dump()))
        self.session.commit()
        self.session.refresh(orm)
        invalidate_all(self.PREFIX)
        return PipelineStageRead.model_validate(orm)

    def update(self, sid: uuid.UUID, payload: PipelineStageUpdate) -> PipelineStageRead:
        orm = self.repo.get(sid)
        if orm is None:
            raise ValueError(f"PipelineStage {sid} not found")
        data = payload.model_dump(exclude_unset=True)
        if "pipeline_id" in data and self.pipe_repo.get(data["pipeline_id"]) is None:
            raise ValueError("Pipeline not found")
        for f, v in data.items():
            setattr(orm, f, v)
        self.session.commit()
        self.session.refresh(orm)
        invalidate_item(self.PREFIX, sid)
        return PipelineStageRead.model_validate(orm)

    def delete(self, sid: uuid.UUID) -> None:
        orm = self.repo.get(sid)
        if orm is None:
            raise ValueError(f"PipelineStage {sid} not found")
        if orm.deals:
            raise ValueError("Cannot delete stage with deals")
        self.repo.delete(orm)
        self.session.commit()
        invalidate_item(self.PREFIX, sid)