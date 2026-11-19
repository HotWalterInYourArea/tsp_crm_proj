from .schemas import WSNotification


def build_deal_created(evt: dict) -> WSNotification:
    deal_name = evt["deal_name"]
    assigned = evt["assigned_to"]
    creator = evt["created_by"]
    budget = evt.get("budget")

    budget_str = f" Бюджет: {budget:,} ₽." if budget else ""
    return WSNotification(
        event_type="deal.created",
        title="Вам назначена новая сделка",
        body=(
            f"Сделка «{deal_name}» создана пользователем "
            f"{creator.get('name') or creator['user_id']} и назначена на вас."
            f"{budget_str}"
        ),
        priority="high",
        deal_id=evt["deal_id"],
        actor=creator.get("name"),
    )


def build_activity_created(evt: dict, recipient_role: str) -> WSNotification:
    deal_name = evt["deal_name"]
    activity_name = evt["activity_name"]
    author = evt.get("author", {})
    due = evt.get("due_at")

    role_label = "Вы исполнитель" if recipient_role == "assignee" else "Вы супервизор"
    due_str = f" Срок: {due}." if due else ""
    return WSNotification(
        event_type="activity.created",
        title="Новая активность по сделке",
        body=(
            f"По сделке «{deal_name}» создана активность "
            f"«{activity_name}» ({author.get('name') or '—'}). "
            f"{role_label}.{due_str}"
        ),
        priority="normal",
        deal_id=evt["deal_id"],
        activity_id=evt["activity_id"],
        actor=author.get("name"),
    )