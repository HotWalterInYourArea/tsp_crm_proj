import uuid
from sqlalchemy.orm import Session

from db_service.repositories.department_repository import DepartmentRepository
from db_service.repositories.user_repository import UserRepository
from api_service.schemas.department_schema import (
    DepartmentCreate, DepartmentUpdate, DepartmentRead,
)
from api_service.core.cache import cache_get, cache_set, cache_delete_pattern
from api_service.services._cached import (
    get_cached_item, set_cached_item,
    get_cached_list, set_cached_list,
    invalidate_item, invalidate_all,
)
class DepartmentService:
    PREFIX = "departments"

    def __init__(self, session: Session):
        self.session = session
        self.repo = DepartmentRepository(session)
        self.user_repo = UserRepository(session)

    def get(self, dept_id: uuid.UUID) -> DepartmentRead:
        cached = get_cached_item(self.PREFIX, dept_id, DepartmentRead.model_validate)
        if cached is not None:
            return cached

        orm = self.repo.get(dept_id)
        if orm is None:
            raise ValueError(f"Department {dept_id} not found")
        dto = DepartmentRead.model_validate(orm)
        set_cached_item(self.PREFIX, dept_id, dto.model_dump(mode="json"))
        return dto

    def list(self, **kw) -> list[DepartmentRead]:
        cached = get_cached_list(self.PREFIX, kw, DepartmentRead.model_validate)
        if cached is not None:
            return cached

        orms = self.repo.list(**kw)
        dtos = [DepartmentRead.model_validate(o) for o in orms]
        set_cached_list(self.PREFIX, kw, [d.model_dump(mode="json") for d in dtos])
        return dtos

    def create(self, payload: DepartmentCreate) -> DepartmentRead:
        if self.repo.get_by_name(payload.name):
            raise ValueError(f"Department {payload.name!r} already exists")
        if payload.head_user_id and self.user_repo.get(payload.head_user_id) is None:
            raise ValueError("Head user not found")
        orm = self.repo.add(self.repo.model(**payload.model_dump()))
        self.session.commit()
        self.session.refresh(orm)
        invalidate_all(self.PREFIX)
        return DepartmentRead.model_validate(orm)

    def update(self, dept_id: uuid.UUID, payload: DepartmentUpdate) -> DepartmentRead:
        orm = self.repo.get(dept_id)
        if orm is None:
            raise ValueError(f"Department {dept_id} not found")
        data = payload.model_dump(exclude_unset=True)
        if "name" in data and data["name"] != orm.name and self.repo.get_by_name(data["name"]):
            raise ValueError("Department name already in use")
        if "head_user_id" in data and data["head_user_id"] and self.user_repo.get(data["head_user_id"]) is None:
            raise ValueError("Head user not found")
        for f, v in data.items():
            setattr(orm, f, v)
        self.session.commit()
        self.session.refresh(orm)
        invalidate_item(self.PREFIX, dept_id)
        return DepartmentRead.model_validate(orm)

    def delete(self, dept_id: uuid.UUID) -> None:
        orm = self.repo.get(dept_id)
        if orm is None:
            raise ValueError(f"Department {dept_id} not found")
        if orm.users:
            raise ValueError("Cannot delete department with users")
        self.repo.delete(orm)
        self.session.commit()
        invalidate_item(self.PREFIX, dept_id)