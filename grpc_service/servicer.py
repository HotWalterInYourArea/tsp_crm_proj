import statistics

from grpc_service.proto import commission_pb2, commission_pb2_grpc


class CommissionServicer(commission_pb2_grpc.CommissionServiceServicer):

    # ---------- 1. Commission ----------
    def CalculateCommission(self, request, context):
        if request.budget < 0:
            context.set_code(3)
            context.set_details("Budget must be non-negative")
            return commission_pb2.CommissionResponse()

        rate = request.rate

        if request.user_role == "Администратор":
            rate *= 0.5         
        elif request.user_role == "Руководитель отдела":
            rate *= 1.2          
        elif request.user_role != "Менеджер":
            rate = 0.0           

        amount = int(request.budget * rate)
        return commission_pb2.CommissionResponse(
            commission_amount=amount,
            effective_rate=rate,
        )

    def CalculateDepartmentBonus(self, request, context):
        total = sum(request.deal_budgets)
        head_bonus = int(total * 0.05)                   
        remaining = total - head_bonus
        per_user = int(remaining / max(request.user_count - 1, 1))
        return commission_pb2.DepartmentBonusResponse(
            total_budget=total,
            head_bonus=head_bonus,
            per_user_bonus=per_user,
        )


    def ForecastBudget(self, request, context):
        history = list(request.monthly_totals)
        if len(history) < 2:
            context.set_code(3)
            context.set_details("Need at least 2 months of history")
            return commission_pb2.ForecastResponse()

        n = len(history)
        xs = list(range(n))
        mean_x = sum(xs) / n
        mean_y = sum(history) / n

        numerator = sum((xs[i] - mean_x) * (history[i] - mean_y) for i in range(n))
        denominator = sum((x - mean_x) ** 2 for x in xs)
        slope = numerator / denominator if denominator else 0
        intercept = mean_y - slope * mean_x

        forecast = [
            max(0, int(intercept + slope * (n + i)))
            for i in range(request.months_ahead)
        ]
        return commission_pb2.ForecastResponse(forecast=forecast, trend=slope)