import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api_service.core.deps import get_current_user, require_admin
from db_service.session import get_db
from api_service.services.activity_service import ActivityTypeService
from api_service.schemas.activity_schema import (
    ActivityTypeCreate, ActivityTypeRead, ActivityTypeUpdate,
)

router = APIRouter(prefix="/activity-types", tags=["activity-types"])


@router.get("", response_model=list[ActivityTypeRead], dependencies=[Depends(get_current_user)])
def list_types(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return ActivityTypeService(db).list(offset=offset, limit=limit)


@router.get("/{tid}", response_model=ActivityTypeRead, dependencies=[Depends(get_current_user)])
def get_type(tid: uuid.UUID, db: Session = Depends(get_db)):
    try:
        return ActivityTypeService(db).get(tid)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("", response_model=ActivityTypeRead, status_code=201, dependencies=[Depends(require_admin)])
def create_type(payload: ActivityTypeCreate, db: Session = Depends(get_db)):
    try:
        return ActivityTypeService(db).create(payload)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.patch("/{tid}", response_model=ActivityTypeRead, dependencies=[Depends(require_admin)])
def update_type(tid: uuid.UUID, payload: ActivityTypeUpdate, db: Session = Depends(get_db)):
    try:
        return ActivityTypeService(db).update(tid, payload)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.delete("/{tid}", status_code=204, dependencies=[Depends(require_admin)])
def delete_type(tid: uuid.UUID, db: Session = Depends(get_db)):
    try:
        ActivityTypeService(db).delete(tid)
    except ValueError as e:
        raise HTTPException(400, str(e))