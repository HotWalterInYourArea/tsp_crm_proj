import grpc
from typing import Iterable
import os
from grpc_service.proto import commission_pb2, commission_pb2_grpc
from api_service.core.config import settings

_channel: grpc.Channel | None = None
_stub: commission_pb2_grpc.CommissionServiceStub | None = None


def _get_stub() -> commission_pb2_grpc.CommissionServiceStub:
    global _channel, _stub
    if _stub is None:
        # settings.GRPC_TARGET is guaranteed to exist because of pydantic validation
        _channel = grpc.insecure_channel(settings.GRPC_TARGET)
        _stub = commission_pb2_grpc.CommissionServiceStub(_channel)
    return _stub


class CommissionClient:
    def calculate_commission(self, budget: int, rate: float, user_role: str) -> dict:
        stub = _get_stub()
        response = stub.CalculateCommission(
            commission_pb2.CommissionRequest(
                budget=budget, rate=rate, user_role=user_role,
            ),
            timeout=3.0,
        )
        return {
            "commission_amount": response.commission_amount,
            "effective_rate": response.effective_rate,
        }

    def calculate_department_bonus(
        self, deal_budgets: Iterable[int], user_count: int,
    ) -> dict:
        stub = _get_stub()
        response = stub.CalculateDepartmentBonus(
            commission_pb2.DepartmentBonusRequest(
                deal_budgets=list(deal_budgets),
                user_count=user_count,
            ),
            timeout=3.0,
        )
        return {
            "total_budget": response.total_budget,
            "head_bonus": response.head_bonus,
            "per_user_bonus": response.per_user_bonus,
        }

    def forecast_budget(self, monthly_totals: Iterable[int], months_ahead: int) -> dict:
        stub = _get_stub()
        response = stub.ForecastBudget(
            commission_pb2.ForecastRequest(
                monthly_totals=list(monthly_totals),
                months_ahead=months_ahead,
            ),
            timeout=3.0,
        )
        return {
            "forecast": list(response.forecast),
            "trend": response.trend,
        }