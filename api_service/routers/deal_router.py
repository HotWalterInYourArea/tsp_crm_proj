import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api_service.core.deps import get_current_user
from db_service.session import get_db
from api_service.services.deal_service import DealService
from api_service.schemas.deal_schema import DealCreate, DealRead, DealUpdate

router = APIRouter(prefix="/deals", tags=["deals"])


@router.get("", response_model=list[DealRead], dependencies=[Depends(get_current_user)])
def list_deals(
    offset: int = 0,
    limit: int = Query(default=100, le=1000),
    pipeline_id: uuid.UUID | None = None,
    pipeline_stage_id: uuid.UUID | None = None,
    assigned_by_id: uuid.UUID | None = None,
    main_client_id: uuid.UUID | None = None,
    name_contains: str | None = None,
    min_budget: int | None = None,
    max_budget: int | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
    order_by: str = "date_created",
    order_desc: bool = True,
    db: Session = Depends(get_db),
):
    return DealService(db).list(
        offset=offset, limit=limit,
        pipeline_id=pipeline_id,
        pipeline_stage_id=pipeline_stage_id,
        assigned_by_id=assigned_by_id,
        main_client_id=main_client_id,
        name_contains=name_contains,
        min_budget=min_budget,
        max_budget=max_budget,
        created_from=created_from, created_to=created_to,
        order_by=order_by, order_desc=order_desc,
    )


@router.get("/stats")
def deal_stats(
    pipeline_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    svc = DealService(db)
    return {
        "count": svc.count(pipeline_id=pipeline_id),
        "total_budget": svc.total_budget(pipeline_id=pipeline_id),
    }


@router.get("/{deal_id}", response_model=DealRead, dependencies=[Depends(get_current_user)])
def get_deal(deal_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        return DealService(db).get(deal_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("", response_model=DealRead, status_code=201, dependencies=[Depends(get_current_user)])
def create_deal(payload: DealCreate, db: Session = Depends(get_db)):
    try:
        return DealService(db).create(payload)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.patch("/{deal_id}", response_model=DealRead, dependencies=[Depends(get_current_user)])
def update_deal(deal_id: uuid.UUID, payload: DealUpdate, db: Session = Depends(get_db)):
    try:
        return DealService(db).update(deal_id, payload)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.delete("/{deal_id}", status_code=204, dependencies=[Depends(get_current_user)])
def delete_deal(deal_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        DealService(db).delete(deal_id)
    except ValueError as e:
        raise HTTPException(404, str(e))