import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api_service.core.deps import get_current_user, require_admin
from db_service.session import get_db
from api_service.services.department_service import DepartmentService
from api_service.schemas.department_schema import (
    DepartmentCreate, DepartmentRead, DepartmentUpdate,
)

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("", response_model=list[DepartmentRead], dependencies=[Depends(get_current_user)])
def list_departments(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return DepartmentService(db).list(offset=offset, limit=limit)


@router.get("/{dept_id}", response_model=DepartmentRead, dependencies=[Depends(get_current_user)])
def get_department(dept_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        return DepartmentService(db).get(dept_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("", response_model=DepartmentRead, status_code=201, dependencies=[Depends(require_admin)])
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db)):
    try:
        return DepartmentService(db).create(payload)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.patch("/{dept_id}", response_model=DepartmentRead, dependencies=[Depends(require_admin)])
def update_department(dept_id: uuid.UUID, payload: DepartmentUpdate, db: Session = Depends(get_db)):
    try:
        return DepartmentService(db).update(dept_id, payload)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.delete("/{dept_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_department(dept_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        DepartmentService(db).delete(dept_id)
    except ValueError as e:
        raise HTTPException(400, str(e))