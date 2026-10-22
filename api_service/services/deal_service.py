import uuid
from sqlalchemy.orm import Session

from db_service.models.client import Client
from db_service.models.user import User
from db_service.repositories.client_repository import ClientRepository
from db_service.repositories.deal_repository import DealRepository
from db_service.repositories.pipeline_repository import PipelineRepository, PipelineStageRepository
from db_service.repositories.user_repository import UserRepository
from api_service.schemas.deal_schema import DealCreate, DealUpdate, DealRead


class DealService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = DealRepository(session)
        self.client_repo = ClientRepository(session)
        self.user_repo = UserRepository(session)
        self.pipe_repo = PipelineRepository(session)
        self.stage_repo = PipelineStageRepository(session)


    def get(self, deal_id: uuid.UUID) -> DealRead:
        orm = self.repo.get(deal_id)
        if orm is None:
            raise ValueError(f"Deal {deal_id} not found")
        return DealRead.model_validate(orm)

    def list(self, **kw) -> list[DealRead]:
        return [DealRead.model_validate(o) for o in self.repo.list(**kw)]

    def count(self, **kw) -> int:
        return self.repo.count(**kw)

    def total_budget(self, **kw) -> int:
        return self.repo.total_budget(**kw)


    def create(self, payload: DealCreate) -> DealRead:
        self._validate_refs(payload)

        orm = self.repo.model(
            name=payload.name,
            main_client_id=payload.main_client_id,
            assigned_by_id=payload.assigned_by_id,
            created_by_id=payload.created_by_id,
            pipeline_id=payload.pipeline_id,
            pipeline_stage_id=payload.pipeline_stage_id,
            budget=payload.budget,
        )
        if payload.contact_client_ids:
            orm.contact_clients = self._load_clients(payload.contact_client_ids)
        if payload.supervisor_ids:
            orm.supervised_by = self._load_users(payload.supervisor_ids)

        self.repo.add(orm)
        self.session.commit()
        self.session.refresh(orm)
        return DealRead.model_validate(orm)

    def update(self, deal_id: uuid.UUID, payload: DealUpdate) -> DealRead:
        orm = self.repo.get(deal_id)
        if orm is None:
            raise ValueError(f"Deal {deal_id} not found")

        data = payload.model_dump(
            exclude_unset=True,
            exclude={"contact_client_ids", "supervisor_ids"},
        )
        if "main_client_id" in data and self.client_repo.get(data["main_client_id"]) is None:
            raise ValueError("Main client not found")
        if "pipeline_id" in data and self.pipe_repo.get(data["pipeline_id"]) is None:
            raise ValueError("Pipeline not found")
        if "pipeline_stage_id" in data and self.stage_repo.get(data["pipeline_stage_id"]) is None:
            raise ValueError("Pipeline stage not found")

        for f, v in data.items():
            setattr(orm, f, v)

        if payload.contact_client_ids is not None:
            orm.contact_clients = self._load_clients(payload.contact_client_ids)
        if payload.supervisor_ids is not None:
            orm.supervised_by = self._load_users(payload.supervisor_ids)

        self.session.commit()
        self.session.refresh(orm)
        return DealRead.model_validate(orm)

    def delete(self, deal_id: uuid.UUID) -> None:
        orm = self.repo.get(deal_id)
        if orm is None:
            raise ValueError(f"Deal {deal_id} not found")
        self.repo.delete(orm)
        self.session.commit()


    def _validate_refs(self, payload: DealCreate) -> None:
        if self.client_repo.get(payload.main_client_id) is None:
            raise ValueError("Main client not found")
        if self.user_repo.get(payload.assigned_by_id) is None:
            raise ValueError("Assigned user not found")
        if self.user_repo.get(payload.created_by_id) is None:
            raise ValueError("Creator not found")
        if self.pipe_repo.get(payload.pipeline_id) is None:
            raise ValueError("Pipeline not found")
        if self.stage_repo.get(payload.pipeline_stage_id) is None:
            raise ValueError("Pipeline stage not found")

    def _load_clients(self, ids: list[uuid.UUID]) -> list[Client]:
        if not ids:
            return []
        clients = [self.client_repo.get(i) for i in ids]
        if any(c is None for c in clients):
            raise ValueError("Some client IDs do not exist")
        return clients

    def _load_users(self, ids: list[uuid.UUID]) -> list[User]:
        if not ids:
            return []
        users = [self.user_repo.get(i) for i in ids]
        if any(u is None for u in users):
            raise ValueError("Some user IDs do not exist")
        return users  