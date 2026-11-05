import uuid
from sqlalchemy.orm import Session

from db_service.repositories.activity_repository import ActivityRepository, ActivityTypeRepository
from db_service.repositories.deal_repository import DealRepository
from db_service.repositories.user_repository import UserRepository
from api_service.schemas.activity_schema import (
    ActivityCreate, ActivityUpdate, ActivityRead,
    ActivityTypeCreate, ActivityTypeUpdate, ActivityTypeRead,
)
from api_service.services._cached import (
    get_cached_item, set_cached_item,
    get_cached_list, set_cached_list,
    invalidate_item, invalidate_all,
)

class ActivityTypeService:
    PREFIX = "activity_types"

    def __init__(self, session: Session):
        self.session = session
        self.repo = ActivityTypeRepository(session)

    def get(self, tid: uuid.UUID) -> ActivityTypeRead:
        cached = get_cached_item(self.PREFIX, tid, ActivityTypeRead.model_validate)
        if cached is not None:
            return cached

        orm = self.repo.get(tid)
        if orm is None:
            raise ValueError(f"ActivityType {tid} not found")
        dto = ActivityTypeRead.model_validate(orm)
        set_cached_item(self.PREFIX, tid, dto.model_dump(mode="json"))
        return dto

    def list(self, **kw) -> list[ActivityTypeRead]:
        cached = get_cached_list(self.PREFIX, kw, ActivityTypeRead.model_validate)
        if cached is not None:
            return cached

        orms = self.repo.list(**kw)
        dtos = [ActivityTypeRead.model_validate(o) for o in orms]
        set_cached_list(self.PREFIX, kw, [d.model_dump(mode="json") for d in dtos])
        return dtos

    def create(self, payload: ActivityTypeCreate) -> ActivityTypeRead:
        if self.repo.get_by_name(payload.name):
            raise ValueError(f"ActivityType {payload.name!r} already exists")
        orm = self.repo.add(self.repo.model(**payload.model_dump()))
        self.session.commit()
        self.session.refresh(orm)
        invalidate_all(self.PREFIX)
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
        invalidate_item(self.PREFIX, tid)
        return ActivityTypeRead.model_validate(orm)

    def delete(self, tid: uuid.UUID) -> None:
        orm = self.repo.get(tid)
        if orm is None:
            raise ValueError(f"ActivityType {tid} not found")
        if orm.activities:
            raise ValueError("Cannot delete type with activities")
        self.repo.delete(orm)
        self.session.commit()
        invalidate_item(self.PREFIX, tid)


class ActivityService:
    PREFIX = "activities"

    def __init__(self, session: Session):
        self.session = session
        self.repo = ActivityRepository(session)
        self.deal_repo = DealRepository(session)
        self.user_repo = UserRepository(session)
        self.type_repo = ActivityTypeRepository(session)

    def get(self, aid: uuid.UUID) -> ActivityRead:
        cached = get_cached_item(self.PREFIX, aid, ActivityRead.model_validate)
        if cached is not None:
            return cached

        orm = self.repo.get(aid)
        if orm is None:
            raise ValueError(f"Activity {aid} not found")
        dto = ActivityRead.model_validate(orm)
        set_cached_item(self.PREFIX, aid, dto.model_dump(mode="json"))
        return dto

    def list_by_deal(self, deal_id: uuid.UUID) -> list[ActivityRead]:
        cached = get_cached_list(self.PREFIX, {"deal_id": deal_id}, ActivityRead.model_validate)
        if cached is not None:
            return cached

        orms = self.repo.list_by_deal(deal_id)
        dtos = [ActivityRead.model_validate(o) for o in orms]
        set_cached_list(self.PREFIX, {"deal_id": deal_id}, [d.model_dump(mode="json") for d in dtos])
        return dtos

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
        invalidate_all(self.PREFIX)
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
        invalidate_item(self.PREFIX, aid)
        return ActivityRead.model_validate(orm)

    def delete(self, aid: uuid.UUID) -> None:
        orm = self.repo.get(aid)
        if orm is None:
            raise ValueError(f"Activity {aid} not found")
        self.repo.delete(orm)
        self.session.commit()
        invalidate_item(self.PREFIX, aid)