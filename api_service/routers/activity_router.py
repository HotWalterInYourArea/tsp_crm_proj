import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api_service.core.deps import get_current_user
from db_service.session import get_db
from api_service.services.activity_service import ActivityService
from api_service.schemas.activity_schema import ActivityCreate, ActivityRead, ActivityUpdate

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("", response_model=list[ActivityRead], dependencies=[Depends(get_current_user)])
def list_activities(
    offset: int = 0, limit: int = 100,
    deal_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    activity_type_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
):
    return ActivityService(db).list(
        offset=offset, limit=limit,
        deal_id=deal_id,
        user_id=user_id,
        activity_type_id=activity_type_id,
    )


@router.get("/{aid}", response_model=ActivityRead, dependencies=[Depends(get_current_user)])
def get_activity(aid: uuid.UUID, db: Session = Depends(get_db)):
    try:
        return ActivityService(db).get(aid)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("", response_model=ActivityRead, status_code=201, dependencies=[Depends(get_current_user)])
def create_activity(payload: ActivityCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        return ActivityService(db).create(payload)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.patch("/{aid}", response_model=ActivityRead, dependencies=[Depends(get_current_user)])
def update_activity(aid: uuid.UUID, payload: ActivityUpdate, db: Session = Depends(get_db)):
    try:
        return ActivityService(db).update(aid, payload)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.delete("/{aid}", status_code=204, dependencies=[Depends(get_current_user)])
def delete_activity(aid: uuid.UUID, db: Session = Depends(get_db)):
    try:
        ActivityService(db).delete(aid)
    except ValueError as e:
        raise HTTPException(404, str(e))