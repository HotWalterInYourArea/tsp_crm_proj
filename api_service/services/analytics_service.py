# db_service/services/analytics.py
import uuid
from sqlalchemy.orm import Session

from db_service.repositories.department_repository import DepartmentRepository
from db_service.repositories.deal_repository import DealRepository
from db_service.repositories.user_repository import UserRepository
from grpc_service.client import CommissionClient
from api_service.core.cache import cache_get, cache_set, cache_delete_pattern

class AnalyticsService:
    PREFIX = "analytics"

    def __init__(self, session: Session):
        self.session = session
        self.dept_repo = DepartmentRepository(session)
        self.user_repo = UserRepository(session)
        self.deal_repo = DealRepository(session)
        self.grpc = CommissionClient()

    def get_department_bonus(self, dept_id: uuid.UUID) -> dict:
        key = f"{self.PREFIX}:dept_bonus:{dept_id}"
        cached = cache_get(key)
        if cached is not None:
            return cached

        dept = self.dept_repo.get(dept_id)
        if dept is None:
            raise ValueError(f"Department {dept_id} not found")
        users = self.user_repo.list_by_department(dept_id)
        deals = self.deal_repo.list_by_assigned_users([u.id for u in users])
        budgets = [d.budget for d in deals if d.budget is not None]
        try:
            bonus = self.grpc.calculate_department_bonus(
                deal_budgets=budgets, user_count=max(len(users), 1)
            )
        except Exception as e:
            raise RuntimeError(f"Commission service unavailable: {e}")

        result = {"department": dept.name, **bonus}
        cache_set(key, result, ttl=300)
        return result

    def get_commission_for_deal(self, deal_id: uuid.UUID, rate: float, user_role: str) -> dict:
        key = f"{self.PREFIX}:commission:{deal_id}:{rate}:{user_role}"
        cached = cache_get(key)
        if cached is not None:
            return cached

        deal = self.deal_repo.get(deal_id)
        if deal is None:
            raise ValueError(f"Deal {deal_id} not found")
        if deal.budget is None:
            raise ValueError("Deal has no budget")
        try:
            result = self.grpc.calculate_commission(
                budget=deal.budget, rate=rate, user_role=user_role
            )
        except Exception as e:
            raise RuntimeError(f"Commission service unavailable: {e}")

        response = {
            "deal_id": str(deal_id),
            "deal_name": deal.name,
            "budget": deal.budget,
            **result,
        }
        cache_set(key, response, ttl=300)
        return response

    def get_forecast(self, months_ahead: int = 3) -> dict:
        key = f"{self.PREFIX}:forecast:{months_ahead}"
        cached = cache_get(key)
        if cached is not None:
            return cached

        monthly_totals = self.deal_repo.get_monthly_budget_totals(months_back=6)
        if len(monthly_totals) < 2:
            raise ValueError("Not enough historical data to forecast")
        try:
            result = self.grpc.forecast_budget(
                monthly_totals=monthly_totals, months_ahead=months_ahead
            )
        except Exception as e:
            raise RuntimeError(f"Commission service unavailable: {e}")

        response = {"historical_monthly_totals": monthly_totals, **result}
        cache_set(key, response, ttl=300)
        return response