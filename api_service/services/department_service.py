import uuid
from sqlalchemy.orm import Session

from db_service.repositories.department_repository import DepartmentRepository
from db_service.repositories.user_repository import UserRepository
from api_service.schemas.department_schema import (
    DepartmentCreate, DepartmentUpdate, DepartmentRead,
)


class DepartmentService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = DepartmentRepository(session)
        self.user_repo = UserRepository(session)

    def get(self, dept_id: uuid.UUID) -> DepartmentRead:
        orm = self.repo.get(dept_id)
        if orm is None:
            raise ValueError(f"Department {dept_id} not found")
        return DepartmentRead.model_validate(orm)

    def list(self, **kw) -> list[DepartmentRead]:
        return [DepartmentRead.model_validate(o) for o in self.repo.list(**kw)]

    def create(self, payload: DepartmentCreate) -> DepartmentRead:
        if self.repo.get_by_name(payload.name):
            raise ValueError(f"Department {payload.name!r} already exists")
        if payload.head_user_id and self.user_repo.get(payload.head_user_id) is None:
            raise ValueError("Head user not found")
        orm = self.repo.add(self.repo.model(**payload.model_dump()))
        self.session.commit()
        self.session.refresh(orm)
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
        return DepartmentRead.model_validate(orm)

    def delete(self, dept_id: uuid.UUID) -> None:
        orm = self.repo.get(dept_id)
        if orm is None:
            raise ValueError(f"Department {dept_id} not found")
        if orm.users:
            raise ValueError("Cannot delete department with users")
        self.repo.delete(orm)
        self.session.commit()