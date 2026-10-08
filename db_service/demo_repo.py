from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from pprint import pprint

from db_service.session import SessionLocal
from db_service.repositories import (
    ActivityRepository,
    ActivityTypeRepository,
    ClientRepository,
    DealRepository,
    DepartmentRepository,
    PipelineRepository,
    PipelineStageRepository,
    UserRepository,
    UserRoleRepository,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def header(title: str) -> None:
    print("\n" + "=" * 78)
    print(f"  {title}")
    print("=" * 78)


def sub(title: str) -> None:
    print(f"\n--- {title} ---")


def show(value, *, label: str | None = None) -> None:
    if label:
        print(f"{label}: ", end="")
    pprint(value, sort_dicts=False, width=100)


# ---------------------------------------------------------------------------
# 1. UserRoleRepository
# ---------------------------------------------------------------------------

def demo_user_role(repo: UserRoleRepository) -> None:
    header("1. UserRoleRepository")

    sub("list() — все роли")
    roles = repo.list(limit=50)
    show([(str(r.id), r.name) for r in roles], label="roles")

    sub("get_by_name('Менеджер')")
    role = repo.get_by_name("Менеджер")
    show((str(role.id), role.name) if role else None)

    sub("list(name_contains='админ')")
    matches = repo.list(name_contains="админ")
    show([r.name for r in matches])

    sub("count() и exists()")
    print(f"total roles          = {repo.count()}")
    if role:
        print(f"exists({role.id})     = {repo.exists(role.id)}")
    print(f"exists(random uuid)  = {repo.exists(uuid.uuid4())}")


# ---------------------------------------------------------------------------
# 2. UserRepository
# ---------------------------------------------------------------------------

def demo_user(
    repo: UserRepository,
    role_repo: UserRoleRepository,
) -> None:
    header("2. UserRepository")

    sub("list() — первые 10")
    users = repo.list(limit=10)
    show([(str(u.id), u.name, u.email) for u in users])

    if not users:
        print("⚠ нет пользователей, пропускаем")
        return

    first = users[0]

    sub("get_by_email / get_by_login")
    by_email = repo.get_by_email(first.email)
    by_login = repo.get_by_login(first.login)
    print(f"get_by_email({first.email!r}) -> {by_email.id if by_email else None}")
    print(f"get_by_login({first.login!r}) -> {by_login.id if by_login else None}")

    sub("list(role_id=...) — фильтр по роли")
    roles = role_repo.list(limit=1)
    if roles:
        by_role = repo.list(role_id=roles[0].id)
        show([u.name for u in by_role], label=f"users with role {roles[0].name!r}")

    sub("list(name_contains='Иван')")
    ivans = repo.list(name_contains="Иван")
    show([u.name for u in ivans])

    sub("list(created_from=..., created_to=...)")
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    recent = repo.list(created_from=week_ago, created_to=now)
    print(f"users created in last 7 days = {len(recent)}")
    ancient = repo.list(
        created_from=datetime(2000, 1, 1, tzinfo=timezone.utc),
        created_to=datetime(2001, 1, 1, tzinfo=timezone.utc),
    )
    print(f"users created in 2000        = {len(ancient)}")

    sub("list(order_by='name', order_desc=False)")
    sorted_users = repo.list(order_by="name", order_desc=False, limit=5)
    show([u.name for u in sorted_users])


# ---------------------------------------------------------------------------
# 3. DepartmentRepository
# ---------------------------------------------------------------------------

def demo_department(repo: DepartmentRepository) -> None:
    header("3. DepartmentRepository")

    sub("list()")
    depts = repo.list(limit=20)
    show([(str(d.id), d.name, str(d.head_user_id) if d.head_user_id else None) for d in depts])

    if not depts:
        print("⚠ нет отделов, пропускаем")
        return

    first = depts[0]

    sub("get_by_name")
    found = repo.get_by_name(first.name)
    print(f"get_by_name({first.name!r}) -> {found.id if found else None}")

    sub("list(name_contains='прод')")
    matches = repo.list(name_contains="прод")
    show([d.name for d in matches])

    if first.head_user_id:
        sub("list_by_head()")
        by_head = repo.list_by_head(first.head_user_id)
        show([d.name for d in by_head])


# ---------------------------------------------------------------------------
# 4. ClientRepository
# ---------------------------------------------------------------------------

def demo_client(repo: ClientRepository) -> None:
    header("4. ClientRepository")

    sub("list() — первые 10")
    clients = repo.list(limit=10)
    show([(str(c.id), c.name, c.email, c.phone) for c in clients])

    if not clients:
        print("⚠ нет клиентов, пропускаем")
        return

    first = clients[0]

    sub("get_by_email / get_by_phone")
    by_email = repo.get_by_email(first.email)
    print(f"get_by_email({first.email!r}) -> {by_email.id if by_email else None}")
    if first.phone:
        by_phone = repo.get_by_phone(first.phone)
        print(f"get_by_phone({first.phone!r}) -> {by_phone.id if by_phone else None}")

    sub("list_by_responsible()")
    by_user = repo.list_by_responsible(first.responsible_user_id)
    show([c.name for c in by_user])

    sub("list(responsible_user_id=...)")
    filtered = repo.list(responsible_user_id=first.responsible_user_id)
    show([c.name for c in filtered])

    sub("list(name_contains='ООО')")
    ooo = repo.list(name_contains="ООО")
    show([c.name for c in ooo])


# ---------------------------------------------------------------------------
# 5. PipelineRepository + PipelineStageRepository
# ---------------------------------------------------------------------------

def demo_pipeline(
    pipe_repo: PipelineRepository,
    stage_repo: PipelineStageRepository,
) -> None:
    header("5. PipelineRepository + PipelineStageRepository")

    sub("Pipeline.list()")
    pipelines = pipe_repo.list(limit=10)
    show([(str(p.id), p.name) for p in pipelines])

    if not pipelines:
        print("⚠ нет воронок, пропускаем")
        return

    first = pipelines[0]

    sub("Pipeline.get_by_name()")
    found = pipe_repo.get_by_name(first.name)
    print(f"get_by_name({first.name!r}) -> {found.id if found else None}")

    sub("PipelineStage.list_by_pipeline()")
    stages = stage_repo.list_by_pipeline(first.id)
    show([(str(s.id), s.name) for s in stages])

    sub("PipelineStage.list(pipeline_id=...)")
    filtered = stage_repo.list(pipeline_id=first.id)
    show([s.name for s in filtered])

    sub("PipelineStage.list(name_contains='нов')")
    matches = stage_repo.list(name_contains="нов")
    show([s.name for s in matches])


# ---------------------------------------------------------------------------
# 6. ActivityTypeRepository + ActivityRepository
# ---------------------------------------------------------------------------

def demo_activity(
    type_repo: ActivityTypeRepository,
    act_repo: ActivityRepository,
) -> None:
    header("6. ActivityTypeRepository + ActivityRepository")

    sub("ActivityType.list()")
    types = type_repo.list(limit=20)
    show([(str(t.id), t.name) for t in types])

    if types:
        sub("ActivityType.get_by_name()")
        t = types[0]
        found = type_repo.get_by_name(t.name)
        print(f"get_by_name({t.name!r}) -> {found.id if found else None}")

    sub("Activity.list() — последние 10")
    activities = act_repo.list(limit=10)
    show([
        (str(a.id), str(a.activity_type_id), str(a.deal_id), str(a.user_id),
         a.description, a.deadline_at)
        for a in activities
    ])

    if not activities:
        print("⚠ нет активностей, пропускаем")
        return

    first = activities[0]

    sub("list_by_deal()")
    by_deal = act_repo.list_by_deal(first.deal_id)
    print(f"activities for deal {first.deal_id} = {len(by_deal)}")
    show([(a.description, a.deadline_at) for a in by_deal])

    sub("list_by_user()")
    by_user = act_repo.list_by_user(first.user_id)
    print(f"activities by user {first.user_id} = {len(by_user)}")

    if first.activity_type_id:
        sub("list_by_type()")
        by_type = act_repo.list_by_type(first.activity_type_id)
        print(f"activities of type {first.activity_type_id} = {len(by_type)}")

    sub("list(has_deadline_at=True)")
    with_deadline = act_repo.list(has_deadline_at=True)
    print(f"activities with deadline = {len(with_deadline)}")
    show([(a.description, a.deadline_at) for a in with_deadline[:5]])

    sub("list(has_deadline_at=False)")
    without_deadline = act_repo.list(has_deadline_at=False)
    print(f"activities without deadline = {len(without_deadline)}")

    sub("list_with_pending_deadline(now + 90 days)")
    soon = act_repo.list_with_pending_deadline(
        datetime.now(timezone.utc) + timedelta(days=90)
    )
    print(f"activities with deadline within 90 days = {len(soon)}")
    show([(a.description, a.deadline_at) for a in soon[:5]])

    sub("list(deadline_from=now, deadline_to=now+30d) — фильтр по дедлайну")
    # предполагается, что ActivityRepository.list принимает deadline_from/deadline_to;
    # если нет — раскомментируйте в репозитории, как показано ниже.
    # filtered = act_repo.list(
    #     deadline_from=datetime.now(timezone.utc),
    #     deadline_to=datetime.now(timezone.utc) + timedelta(days=30),
    # )
    # show([(a.description, a.deadline_at) for a in filtered])
    print("(см. ActivityRepository.list — добавьте deadline_from/deadline_to по желанию)")


# ---------------------------------------------------------------------------
# 7. DealRepository — без deadline (у Deal его нет)
# ---------------------------------------------------------------------------

def demo_deal(repo: DealRepository) -> None:
    header("7. DealRepository")

    sub("list() — первые 5")
    deals = repo.list(limit=5)
    show([
        (str(d.id), d.name, d.budget, str(d.pipeline_id), str(d.pipeline_stage_id))
        for d in deals
    ])

    if not deals:
        print("⚠ нет сделок, пропускаем")
        return

    first = deals[0]

    sub("get() — с eager loading контактов, супервизоров, активностей")
    d = repo.get(first.id)
    if d:
        print(f"id         = {d.id}")
        print(f"name       = {d.name!r}")
        print(f"budget     = {d.budget}")
        print(f"contacts   = {[c.name for c in d.contact_clients]}")
        print(f"supervised = {[u.name for u in d.supervised_by]}")
        print(f"activities = {len(d.activities)}")

    sub("list_by_pipeline()")
    by_pipeline = repo.list_by_pipeline(first.pipeline_id)
    print(f"deals in pipeline {first.pipeline_id} = {len(by_pipeline)}")

    sub("list_by_stage()")
    by_stage = repo.list_by_stage(first.pipeline_stage_id)
    print(f"deals in stage {first.pipeline_stage_id} = {len(by_stage)}")

    sub("list_by_client()")
    by_client = repo.list_by_client(first.main_client_id)
    print(f"deals for client {first.main_client_id} = {len(by_client)}")

    sub("list_by_assigned_user()")
    by_user = repo.list_by_assigned_user(first.assigned_by_id)
    print(f"deals assigned to user {first.assigned_by_id} = {len(by_user)}")

    sub("list_by_budget_range(100_000, 1_000_000)")
    by_budget = repo.list_by_budget_range(100_000, 1_000_000)
    show([(d.name, d.budget) for d in by_budget])

    sub("list(min_budget=..., max_budget=...)")
    filtered = repo.list(min_budget=200_000, max_budget=1_500_000)
    show([(d.name, d.budget) for d in filtered])

    sub("list(name_contains='CRM')")
    matches = repo.list(name_contains="CRM")
    show([d.name for d in matches])

    sub("list(created_from=..., created_to=...) — за последние 30 дней")
    now = datetime.now(timezone.utc)
    recent = repo.list(created_from=now - timedelta(days=30), created_to=now)
    print(f"deals created in last 30 days = {len(recent)}")

    sub("list(order_by='budget', order_desc=True) — топ-5 по бюджету")
    top = repo.list(order_by="budget", order_desc=True, limit=5)
    show([(d.name, d.budget) for d in top])

    sub("count() и count(pipeline_id=...)")
    print(f"total deals = {repo.count()}")
    print(f"deals in pipeline {first.pipeline_id} = {repo.count(pipeline_id=first.pipeline_id)}")

    sub("total_budget() и total_budget(pipeline_id=...)")
    print(f"total budget = {repo.total_budget()}")
    print(f"budget in pipeline {first.pipeline_id} = {repo.total_budget(pipeline_id=first.pipeline_id)}")

    sub("count(created_from=...) — за последние 7 дней")
    week_ago = now - timedelta(days=7)
    print(f"deals created last week = {repo.count(created_from=week_ago)}")


# ---------------------------------------------------------------------------
# 8. Полный CRUD-цикл
# ---------------------------------------------------------------------------

def demo_crud_cycle(
    *,
    role_repo: UserRoleRepository,
    user_repo: UserRepository,
    client_repo: ClientRepository,
    pipe_repo: PipelineRepository,
    stage_repo: PipelineStageRepository,
    deal_repo: DealRepository,
    act_type_repo: ActivityTypeRepository,
    act_repo: ActivityRepository,
) -> None:
    header("8. Полный CRUD-цикл (rollback в конце)")

    from db_service.models.user import User, UserRole
    from db_service.models.client import Client
    from db_service.models.pipeline import Pipeline, PipelineStage
    from db_service.models.deal import Deal
    from db_service.models.activity import Activity, ActivityType

    sub("CREATE — роль, пользователь, клиент, воронка, стадия, сделка, активность")

    role = UserRole(name=f"Демо-роль-{uuid.uuid4().hex[:6]}")
    role_repo.add(role)

    user = User(
        name="Демо Пользователь",
        email=f"demo-{uuid.uuid4().hex[:6]}@example.com",
        phone="+79001234567",
        login=f"demo_{uuid.uuid4().hex[:6]}",
        hashed_password="hashed_demo",
        role_id=role.id,
    )
    user_repo.add(user)

    client = Client(
        name="ООО Демо-клиент",
        email=f"client-{uuid.uuid4().hex[:6]}@example.com",
        phone="+79007654321",
        responsible_user_id=user.id,
    )
    client_repo.add(client)

    pipeline = Pipeline(name=f"Демо-воронка-{uuid.uuid4().hex[:6]}")
    pipe_repo.add(pipeline)

    stage = PipelineStage(name="Демо-стадия", pipeline_id=pipeline.id)
    stage_repo.add(stage)

    deal = Deal(
        name="Демо-сделка",
        main_client_id=client.id,
        assigned_by_id=user.id,
        created_by_id=user.id,
        pipeline_id=pipeline.id,
        pipeline_stage_id=stage.id,
        budget=42_000,
    )
    deal_repo.add(deal)

    atype = ActivityType(name=f"Демо-тип-{uuid.uuid4().hex[:6]}")
    act_type_repo.add(atype)

    activity = Activity(
        description="Демо-звонок",
        activity_type_id=atype.id,
        deal_id=deal.id,
        user_id=user.id,
        deadline_at=datetime.now(timezone.utc) + timedelta(days=5),  # ← deadline_at
    )
    act_repo.add(activity)

    print(f"✔ role      = {role.id}")
    print(f"✔ user      = {user.id}")
    print(f"✔ client    = {client.id}")
    print(f"✔ pipeline  = {pipeline.id}")
    print(f"✔ stage     = {stage.id}")
    print(f"✔ deal      = {deal.id}")
    print(f"✔ activity  = {activity.id}")

    sub("READ — читаем обратно из БД")
    read_deal = deal_repo.get(deal.id)
    print(f"deal.name       = {read_deal.name!r}")
    print(f"deal.client     = {read_deal.main_client.name!r}")
    print(f"deal.user       = {read_deal.assigned_by.name!r}")
    print(f"deal.stage      = {read_deal.pipeline_stage.name!r}")
    print(f"deal.budget     = {read_deal.budget}")

    read_act = act_repo.get(activity.id)
    print(f"act.description = {read_act.description!r}")
    print(f"act.deadline_at = {read_act.deadline_at}")

    sub("UPDATE — меняем бюджет, стадию и дедлайн активности")
    read_deal.budget = 99_000
    stage2 = PipelineStage(name="Демо-стадия-2", pipeline_id=pipeline.id)
    stage_repo.add(stage2)
    read_deal.pipeline_stage_id = stage2.id

    read_act.deadline_at = datetime.now(timezone.utc) + timedelta(days=30)

    session = deal_repo.session
    session.flush()

    refreshed_deal = deal_repo.get(deal.id)
    refreshed_act = act_repo.get(activity.id)
    print(f"deal.budget       = {refreshed_deal.budget}")
    print(f"deal.stage        = {refreshed_deal.pipeline_stage.name!r}")
    print(f"deal.updated_at = {refreshed_deal.updated_at}")
    print(f"act.deadline_at   = {refreshed_act.deadline_at}")

    sub("DELETE — удаляем сделку (каскадно удалит активности)")
    deal_repo.delete(refreshed_deal)
    session.flush()
    print(f"deal exists after delete     = {deal_repo.exists(deal.id)}")
    print(f"activity exists after delete = {act_repo.exists(activity.id)}")

    sub("Не коммитим — транзакция будет откачена")
    session.rollback()
    print("✔ rollback выполнен")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> None:
    with SessionLocal() as session:
        role_repo     = UserRoleRepository(session)
        user_repo     = UserRepository(session)
        dept_repo     = DepartmentRepository(session)
        client_repo   = ClientRepository(session)
        pipe_repo     = PipelineRepository(session)
        stage_repo    = PipelineStageRepository(session)
        act_type_repo = ActivityTypeRepository(session)
        act_repo      = ActivityRepository(session)
        deal_repo     = DealRepository(session)

        demo_user_role(role_repo)
        demo_user(user_repo, role_repo)
        demo_department(dept_repo)
        demo_client(client_repo)
        demo_pipeline(pipe_repo, stage_repo)
        demo_activity(act_type_repo, act_repo)
        demo_deal(deal_repo)
        demo_crud_cycle(
            role_repo=role_repo,
            user_repo=user_repo,
            client_repo=client_repo,
            pipe_repo=pipe_repo,
            stage_repo=stage_repo,
            deal_repo=deal_repo,
            act_type_repo=act_type_repo,
            act_repo=act_repo,
        )

    print("\n🎉 Демонстрация завершена. Изменения не сохранены.")


if __name__ == "__main__":
    main()