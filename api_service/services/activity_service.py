import uuid
from sqlalchemy.orm import Session

from db_service.repositories.activity_repository import ActivityRepository, ActivityTypeRepository
from db_service.repositories.deal_repository import DealRepository
from db_service.repositories.user_repository import UserRepository
from api_service.schemas.activity_schema import (
    ActivityCreate, ActivityUpdate, ActivityRead,
    ActivityTypeCreate, ActivityTypeUpdate, ActivityTypeRead,
)


class ActivityTypeService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = ActivityTypeRepository(session)

    def get(self, tid: uuid.UUID) -> ActivityTypeRead:
        orm = self.repo.get(tid)
        if orm is None:
            raise ValueError(f"ActivityType {tid} not found")
        return ActivityTypeRead.model_validate(orm)

    def list(self, **kw) -> list[ActivityTypeRead]:
        return [ActivityTypeRead.model_validate(o) for o in self.repo.list(**kw)]

    def create(self, payload: ActivityTypeCreate) -> ActivityTypeRead:
        if self.repo.get_by_name(payload.name):
            raise ValueError(f"ActivityType {payload.name!r} already exists")
        orm = self.repo.add(self.repo.model(**payload.model_dump()))
        self.session.commit()
        self.session.refresh(orm)
        return ActivityTypeRead.model_validate(orm)

    def update(self, tid: uuid.UUID, payload: ActivityTypeUpdate) -> ActivityTypeRead:
        orm = self.repo.get(tid)
        if orm is None:
            raise ValueError(f"ActivityType {tid} not found")
        data = payload.model_dump(exclude_unset=True)
        if "name" in data and data["name"] != orm.name and self.repo.get_by_name(data["name"]):
            raise ValueError("Name already in use")
        for f, v in data.items():
            setattr(orm, f, v)
        self.session.commit()
        self.session.refresh(orm)
        return ActivityTypeRead.model_validate(orm)

    def delete(self, tid: uuid.UUID) -> None:
        orm = self.repo.get(tid)
        if orm is None:
            raise ValueError(f"ActivityType {tid} not found")
        if orm.activities:
            raise ValueError("Cannot delete type with activities")
        self.repo.delete(orm)
        self.session.commit()


class ActivityService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = ActivityRepository(session)
        self.deal_repo = DealRepository(session)
        self.user_repo = UserRepository(session)
        self.type_repo = ActivityTypeRepository(session)

    def get(self, aid: uuid.UUID) -> ActivityRead:
        orm = self.repo.get(aid)
        if orm is None:
            raise ValueError(f"Activity {aid} not found")
        return ActivityRead.model_validate(orm)

    def list(self, **kw) -> list[ActivityRead]:
        return [ActivityRead.model_validate(o) for o in self.repo.list(**kw)]

    def list_by_deal(self, deal_id: uuid.UUID) -> list[ActivityRead]:
        return [ActivityRead.model_validate(o) for o in self.repo.list_by_deal(deal_id)]

    def create(self, payload: ActivityCreate) -> ActivityRead:
        if self.deal_repo.get(payload.deal_id) is None:
            raise ValueError("Deal not found")
        if self.user_repo.get(payload.user_id) is None:
            raise ValueError("User not found")
        if payload.activity_type_id and self.type_repo.get(payload.activity_type_id) is None:
            raise ValueError("ActivityType not found")
        orm = self.repo.add(self.repo.model(**payload.model_dump()))
        self.session.commit()
        self.session.refresh(orm)
        return ActivityRead.model_validate(orm)

    def update(self, aid: uuid.UUID, payload: ActivityUpdate) -> ActivityRead:
        orm = self.repo.get(aid)
        if orm is None:
            raise ValueError(f"Activity {aid} not found")
        data = payload.model_dump(exclude_unset=True)
        if "deal_id" in data and self.deal_repo.get(data["deal_id"]) is None:
            raise ValueError("Deal not found")
        if "user_id" in data and self.user_repo.get(data["user_id"]) is None:
            raise ValueError("User not found")
        if "activity_type_id" in data and data["activity_type_id"] and self.type_repo.get(data["activity_type_id"]) is None:
            raise ValueError("ActivityType not found")
        for f, v in data.items():
            setattr(orm, f, v)
        self.session.commit()
        self.session.refresh(orm)
        return ActivityRead.model_validate(orm)

    def delete(self, aid: uuid.UUID) -> None:
        orm = self.repo.get(aid)
        if orm is None:
            raise ValueError(f"Activity {aid} not found")
        self.repo.delete(orm)
        self.session.commit()