from __future__ import annotations

from datetime import datetime, timedelta, timezone

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
from db_service.models.user import User, UserRole
from db_service.models.department import Department
from db_service.models.client import Client
from db_service.models.pipeline import Pipeline, PipelineStage
from db_service.models.activity import Activity, ActivityType
from db_service.models.deal import Deal


# ---------------------------------------------------------------------------
# helpers — get-or-create for idempotency
# ---------------------------------------------------------------------------

def _get_or_create_role(repo: UserRoleRepository, name: str) -> UserRole:
    role = repo.get_by_name(name)
    if role is None:
        role = UserRole(name=name)
        repo.add(role)
        print(f"  + role       {name!r}")
    else:
        print(f"  = role       {name!r} (exists)")
    return role


def _get_or_create_department(repo: DepartmentRepository, name: str) -> Department:
    dept = repo.get_by_name(name)
    if dept is None:
        dept = Department(name=name)
        repo.add(dept)
        print(f"  + dept       {name!r}")
    else:
        print(f"  = dept       {name!r} (exists)")
    return dept


def _get_or_create_user(
    repo: UserRepository,
    *,
    name: str,
    email: str,
    phone: str | None,
    login: str,
    hashed_password: str,
    role_id,
    department_id=None,
) -> User:
    user = repo.get_by_login(login)
    if user is None:
        user = User(
            name=name,
            email=email,
            phone=phone,
            login=login,
            hashed_password=hashed_password,
            role_id=role_id,
            department_id=department_id,
        )
        repo.add(user)
        print(f"  + user       {login!r}")
    else:
        print(f"  = user       {login!r} (exists)")
    return user


def _get_or_create_client(
    repo: ClientRepository,
    *,
    name: str,
    email: str,
    phone: str | None,
    responsible_user_id,
) -> Client:
    client = repo.get_by_email(email)
    if client is None:
        client = Client(
            name=name,
            email=email,
            phone=phone,
            responsible_user_id=responsible_user_id,
        )
        repo.add(client)
        print(f"  + client     {name!r}")
    else:
        print(f"  = client     {name!r} (exists)")
    return client


def _get_or_create_pipeline(repo: PipelineRepository, name: str) -> Pipeline:
    pipeline = repo.get_by_name(name)
    if pipeline is None:
        pipeline = Pipeline(name=name)
        repo.add(pipeline)
        print(f"  + pipeline   {name!r}")
    else:
        print(f"  = pipeline   {name!r} (exists)")
    return pipeline


def _get_or_create_stage(
    repo: PipelineStageRepository,
    *,
    name: str,
    pipeline_id,
) -> PipelineStage:
    # у PipelineStage нет get_by_name — ищем по списку стадий воронки
    for s in repo.list_by_pipeline(pipeline_id):
        if s.name == name:
            print(f"  = stage      {name!r} (exists)")
            return s
    stage = PipelineStage(name=name, pipeline_id=pipeline_id)
    repo.add(stage)
    print(f"  + stage      {name!r}")
    return stage


def _get_or_create_activity_type(
    repo: ActivityTypeRepository, name: str
) -> ActivityType:
    t = repo.get_by_name(name)
    if t is None:
        t = ActivityType(name=name)
        repo.add(t)
        print(f"  + act.type   {name!r}")
    else:
        print(f"  = act.type   {name!r} (exists)")
    return t


def _get_or_create_deal(
    repo: DealRepository,
    *,
    name: str,
    main_client_id,
    assigned_by_id,
    created_by_id,
    pipeline_id,
    pipeline_stage_id,
    budget: int | None = None,
) -> Deal:
    # точное совпадение по имени, иначе list(name_contains=...) вернёт лишнее
    matches = repo.list(name_contains=name, limit=5)
    for m in matches:
        if m.name == name:
            print(f"  = deal       {name!r} (exists)")
            return m
    deal = Deal(
        name=name,
        main_client_id=main_client_id,
        assigned_by_id=assigned_by_id,
        created_by_id=created_by_id,
        pipeline_id=pipeline_id,
        pipeline_stage_id=pipeline_stage_id,
        budget=budget,
    )
    repo.add(deal)
    print(f"  + deal       {name!r}")
    return deal


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def seed() -> None:
    with SessionLocal() as session:
        # --- repositories ---
        role_repo      = UserRoleRepository(session)
        user_repo      = UserRepository(session)
        dept_repo      = DepartmentRepository(session)
        client_repo    = ClientRepository(session)
        pipe_repo      = PipelineRepository(session)
        stage_repo     = PipelineStageRepository(session)
        act_type_repo  = ActivityTypeRepository(session)
        act_repo       = ActivityRepository(session)
        deal_repo      = DealRepository(session)

        # --- roles ---
        print("→ Роли")
        role_admin = _get_or_create_role(role_repo, "Администратор")
        role_manager = _get_or_create_role(role_repo, "Менеджер")
        session.flush()

        # --- departments ---
        print("→ Отделы")
        dept_sales = _get_or_create_department(dept_repo, "Отдел продаж")
        session.flush()

        # --- users ---
        print("→ Пользователи")
        admin = _get_or_create_user(
            user_repo,
            name="Админ Админович",
            email="admin@example.com",
            phone="+79001112233",
            login="admin",
            hashed_password="hashed_admin",
            role_id=role_admin.id,
            department_id=dept_sales.id,
        )
        manager = _get_or_create_user(
            user_repo,
            name="Иван Менеджеров",
            email="ivan@example.com",
            phone="+79004445566",
            login="ivan",
            hashed_password="hashed_ivan",
            role_id=role_manager.id,
            department_id=dept_sales.id,
        )
        supervisor = _get_or_create_user(
            user_repo,
            name="Пётр Руководителев",
            email="petr@example.com",
            phone="+79007778899",
            login="petr",
            hashed_password="hashed_petr",
            role_id=role_manager.id,
            department_id=dept_sales.id,
        )
        session.flush()

        # назначить руководителя отдела
        if dept_sales.head_user_id is None:
            dept_sales.head_user_id = supervisor.id
            print(f"  ~ dept       {dept_sales.name!r} head → {supervisor.login!r}")

        # --- clients ---
        print("→ Клиенты")
        client_a = _get_or_create_client(
            client_repo,
            name="ООО Ромашка",
            email="romashka@example.com",
            phone="+79001234567",
            responsible_user_id=manager.id,
        )
        client_b = _get_or_create_client(
            client_repo,
            name="ИП Иванов",
            email="ivanov@example.com",
            phone="+79007654321",
            responsible_user_id=manager.id,
        )
        client_c = _get_or_create_client(
            client_repo,
            name="ООО Лютик",
            email="lyutik@example.com",
            phone="+79005555555",
            responsible_user_id=manager.id,
        )
        session.flush()

        # --- pipeline + stages ---
        print("→ Воронка и стадии")
        pipeline = _get_or_create_pipeline(pipe_repo, "Основная воронка продаж")
        session.flush()

        stage_new = _get_or_create_stage(stage_repo, name="Новая", pipeline_id=pipeline.id)
        stage_neg = _get_or_create_stage(stage_repo, name="Переговоры", pipeline_id=pipeline.id)
        stage_won = _get_or_create_stage(stage_repo, name="Успешно", pipeline_id=pipeline.id)
        session.flush()

        # --- activity types ---
        print("→ Типы активностей")
        t_call  = _get_or_create_activity_type(act_type_repo, "Звонок")
        t_meet  = _get_or_create_activity_type(act_type_repo, "Встреча")
        t_email = _get_or_create_activity_type(act_type_repo, "Email")
        session.flush()

        # --- deals (без deadline — его у Deal нет) ---
        print("→ Сделки")
        deal1 = _get_or_create_deal(
            deal_repo,
            name="Поставка офисной мебели",
            main_client_id=client_a.id,
            assigned_by_id=manager.id,
            created_by_id=admin.id,
            pipeline_id=pipeline.id,
            pipeline_stage_id=stage_neg.id,
            budget=500_000,
        )
        deal2 = _get_or_create_deal(
            deal_repo,
            name="Разработка CRM",
            main_client_id=client_b.id,
            assigned_by_id=manager.id,
            created_by_id=admin.id,
            pipeline_id=pipeline.id,
            pipeline_stage_id=stage_new.id,
            budget=1_200_000,
        )
        deal3 = _get_or_create_deal(
            deal_repo,
            name="Консалтинг",
            main_client_id=client_c.id,
            assigned_by_id=manager.id,
            created_by_id=admin.id,
            pipeline_id=pipeline.id,
            pipeline_stage_id=stage_won.id,
            budget=150_000,
        )
        session.flush()

        # --- M2M: contact_clients / supervised_by ---
        print("→ M2M-связи")
        if client_b not in deal1.contact_clients:
            deal1.contact_clients.append(client_b)
            print(f"  ~ deal {deal1.name!r} contact_clients += {client_b.name!r}")
        if supervisor not in deal1.supervised_by:
            deal1.supervised_by.append(supervisor)
            print(f"  ~ deal {deal1.name!r} supervised_by  += {supervisor.login!r}")
        session.flush()

        # --- activities (deadline_at — на Activity, не на Deal) ---
        print("→ Активности")
        now = datetime.now(timezone.utc)

        if not act_repo.list_by_deal(deal1.id):
            act_repo.add(Activity(
                deal_id=deal1.id,
                user_id=manager.id,
                activity_type_id=t_call.id,
                description="Обсудили сроки поставки",
                deadline_at=now + timedelta(days=3),
            ))
            act_repo.add(Activity(
                deal_id=deal1.id,
                user_id=manager.id,
                activity_type_id=t_meet.id,
                description="Встреча в офисе клиента",
                deadline_at=now + timedelta(days=7),
            ))
            print("  + 2 activities for 'Поставка офисной мебели'")
        else:
            print("  = activities for 'Поставка офисной мебели' (exist)")

        if not act_repo.list_by_deal(deal2.id):
            act_repo.add(Activity(
                deal_id=deal2.id,
                user_id=manager.id,
                activity_type_id=t_email.id,
                description="Отправили коммерческое предложение",
                deadline_at=now + timedelta(days=14),
            ))
            print("  + 1 activity for 'Разработка CRM'")
        else:
            print("  = activities for 'Разработка CRM' (exist)")

        if not act_repo.list_by_deal(deal3.id):
            act_repo.add(Activity(
                deal_id=deal3.id,
                user_id=supervisor.id,
                activity_type_id=t_meet.id,
                description="Согласование условий консалтинга",
                deadline_at=None,   # без дедлайна — тоже валидный кейс
            ))
            print("  + 1 activity for 'Консалтинг'")
        else:
            print("  = activities for 'Консалтинг' (exist)")

        # --- commit ---
        session.commit()
        print("\n✅ База заполнена тестовыми данными")


if __name__ == "__main__":
    seed()