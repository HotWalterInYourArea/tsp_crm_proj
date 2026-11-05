# api_service/routers/analytics.py
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db_service.session import get_db
from api_service.core.deps import get_current_user
from db_service.models.user import User
from api_service.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/commission/{deal_id}")
def commission_for_deal(
    deal_id: uuid.UUID,
    rate: float = 0.05,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role_name = current_user.user_role.name if current_user.user_role else "Менеджер"
    try:
        return AnalyticsService(db).get_commission_for_deal(
            deal_id=deal_id, rate=rate, user_role=role_name,
        )
    except ValueError as e:
        raise HTTPException(404, str(e))
    except RuntimeError as e:
        raise HTTPException(503, str(e))


@router.get("/department-bonus/{dept_id}")
def department_bonus(
    dept_id: uuid.UUID,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    try:
        return AnalyticsService(db).get_department_bonus(dept_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except RuntimeError as e:
        raise HTTPException(503, str(e))


@router.get("/forecast")
def forecast(
    months_ahead: int = 3,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Forecast future budget based on actual DB history."""
    try:
        return AnalyticsService(db).get_forecast(months_ahead)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except RuntimeError as e:
        raise HTTPException(503, str(e))