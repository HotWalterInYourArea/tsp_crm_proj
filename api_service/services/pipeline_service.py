import uuid
from sqlalchemy.orm import Session

from db_service.repositories.pipeline_repository import PipelineRepository, PipelineStageRepository
from api_service.schemas.pipeline_schema import (
    PipelineCreate, PipelineUpdate, PipelineRead,
    PipelineStageCreate, PipelineStageUpdate, PipelineStageRead,
)


class PipelineService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = PipelineRepository(session)

    def get(self, pid: uuid.UUID) -> PipelineRead:
        orm = self.repo.get(pid)
        if orm is None:
            raise ValueError(f"Pipeline {pid} not found")
        return PipelineRead.model_validate(orm)

    def list(self, **kw) -> list[PipelineRead]:
        return [PipelineRead.model_validate(o) for o in self.repo.list(**kw)]

    def create(self, payload: PipelineCreate) -> PipelineRead:
        if self.repo.get_by_name(payload.name):
            raise ValueError(f"Pipeline {payload.name!r} already exists")
        orm = self.repo.add(self.repo.model(**payload.model_dump()))
        self.session.commit()
        self.session.refresh(orm)
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
        return PipelineRead.model_validate(orm)

    def delete(self, pid: uuid.UUID) -> None:
        orm = self.repo.get(pid)
        if orm is None:
            raise ValueError(f"Pipeline {pid} not found")
        if orm.deals:
            raise ValueError("Cannot delete pipeline with deals")
        self.repo.delete(orm)
        self.session.commit()


class PipelineStageService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = PipelineStageRepository(session)
        self.pipe_repo = PipelineRepository(session)

    def get(self, sid: uuid.UUID) -> PipelineStageRead:
        orm = self.repo.get(sid)
        if orm is None:
            raise ValueError(f"PipelineStage {sid} not found")
        return PipelineStageRead.model_validate(orm)

    def list_by_pipeline(self, pid: uuid.UUID) -> list[PipelineStageRead]:
        return [PipelineStageRead.model_validate(o) for o in self.repo.list_by_pipeline(pid)]

    def create(self, payload: PipelineStageCreate) -> PipelineStageRead:
        if self.pipe_repo.get(payload.pipeline_id) is None:
            raise ValueError("Pipeline not found")
        orm = self.repo.add(self.repo.model(**payload.model_dump()))
        self.session.commit()
        self.session.refresh(orm)
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
        return PipelineStageRead.model_validate(orm)

    def delete(self, sid: uuid.UUID) -> None:
        orm = self.repo.get(sid)
        if orm is None:
            raise ValueError(f"PipelineStage {sid} not found")
        if orm.deals:
            raise ValueError("Cannot delete stage with deals")
        self.repo.delete(orm)
        self.session.commit()