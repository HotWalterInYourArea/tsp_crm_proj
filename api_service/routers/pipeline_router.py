import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api_service.core.deps import get_current_user, require_admin
from db_service.session import get_db
from api_service.services.pipeline_service import PipelineService, PipelineStageService
from api_service.schemas.pipeline_schema import (
    PipelineCreate, PipelineRead, PipelineUpdate,
    PipelineStageCreate, PipelineStageRead, PipelineStageUpdate,
)

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.get("", response_model=list[PipelineRead], dependencies=[Depends(get_current_user)])
def list_pipelines(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return PipelineService(db).list(offset=offset, limit=limit)


@router.get("/{pid}", response_model=PipelineRead, dependencies=[Depends(get_current_user)])
def get_pipeline(pid: uuid.UUID, db: Session = Depends(get_db)):
    try:
        return PipelineService(db).get(pid)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("", response_model=PipelineRead, status_code=201, dependencies=[Depends(require_admin)])
def create_pipeline(payload: PipelineCreate, db: Session = Depends(get_db)):
    try:
        return PipelineService(db).create(payload)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.patch("/{pid}", response_model=PipelineRead, dependencies=[Depends(require_admin)])
def update_pipeline(pid: uuid.UUID, payload: PipelineUpdate, db: Session = Depends(get_db)):
    try:
        return PipelineService(db).update(pid, payload)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.delete("/{pid}", status_code=204, dependencies=[Depends(require_admin)])
def delete_pipeline(pid: uuid.UUID, db: Session = Depends(get_db)):
    try:
        PipelineService(db).delete(pid)
    except ValueError as e:
        raise HTTPException(400, str(e))


# --- stages ---
@router.get("/{pid}/stages", response_model=list[PipelineStageRead], dependencies=[Depends(get_current_user)])
def list_stages(pid: uuid.UUID, db: Session = Depends(get_db)):
    return PipelineStageService(db).list_by_pipeline(pid)


@router.post("/stages", response_model=PipelineStageRead, status_code=201, dependencies=[Depends(require_admin)])
def create_stage(payload: PipelineStageCreate, db: Session = Depends(get_db)):
    try:
        return PipelineStageService(db).create(payload)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.patch("/stages/{sid}", response_model=PipelineStageRead, dependencies=[Depends(require_admin)])
def update_stage(sid: uuid.UUID, payload: PipelineStageUpdate, db: Session = Depends(get_db)):
    try:
        return PipelineStageService(db).update(sid, payload)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.delete("/stages/{sid}", status_code=204, dependencies=[Depends(require_admin)])
def delete_stage(sid: uuid.UUID, db: Session = Depends(get_db)):
    try:
        PipelineStageService(db).delete(sid)
    except ValueError as e:
        raise HTTPException(400, str(e))