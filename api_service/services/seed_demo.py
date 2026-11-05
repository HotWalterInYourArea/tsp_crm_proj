from __future__ import annotations

from datetime import datetime, timezone

from db_service.session import SessionLocal
from api_service.core.security import hash_password
from db_service.repositories import (
    ActivityRepository, ActivityTypeRepository, ClientRepository,
    DealRepository, DepartmentRepository, PipelineRepository,
    PipelineStageRepository, UserRepository, UserRoleRepository,
)
from db_service.models.user import User, UserRole
from db_service.models.department import Department
from db_service.models.client import Client
from db_service.models.pipeline import Pipeline, PipelineStage
from db_service.models.activity import Activity, ActivityType
from db_service.models.deal import Deal


def _get_or_create_role(repo, name):
    obj = repo.get_by_name(name)
    return obj if obj else repo.add(UserRole(name=name))


def _get_or_create_dept(repo, name):
    obj = repo.get_by_name(name)
    return obj if obj else repo.add(Department(name=name))


def _get_or_create_user(repo, *, name, email, phone, login, password, role_id, department_id=None):
    obj = repo.get_by_login(login)
    if obj:
        # ensure hash is valid bcrypt (re-hash if legacy garbage exists)
        if not obj.hashed_password.startswith("$2"):
            obj.hashed_password = hash_password(password)
        return obj
    return repo.add(repo.model(
        name=name, email=email, phone=phone, login=login,
        hashed_password=hash_password(password),
        role_id=role_id, department_id=department_id,
    ))


def _get_or_create_client(repo, *, name, email, phone, responsible_user_id):
    obj = repo.get_by_email(email)
    return obj if obj else repo.add(repo.model(
        name=name, email=email, phone=phone,
        responsible_user_id=responsible_user_id,
    ))


def _get_or_create_pipeline(repo, name):
    obj = repo.get_by_name(name)
    return obj if obj else repo.add(Pipeline(name=name))


def _get_or_create_stage(repo, *, name, pipeline_id):
    for s in repo.list_by_pipeline(pipeline_id):
        if s.name == name:
            return s
    return repo.add(PipelineStage(name=name, pipeline_id=pipeline_id))


def _get_or_create_activity_type(repo, name):
    obj = repo.get_by_name(name)
    return obj if obj else repo.add(ActivityType(name=name))


def _get_or_create_deal(repo, *, name, main_client_id, assigned_by_id,
                        created_by_id, pipeline_id, pipeline_stage_id, budget=None):
    for d in repo.list(name_contains=name, limit=5):
        if d.name == name:
            return d
    return repo.add(repo.model(
        name=name, main_client_id=main_client_id,
        assigned_by_id=assigned_by_id, created_by_id=created_by_id,
        pipeline_id=pipeline_id, pipeline_stage_id=pipeline_stage_id,
        budget=budget,
    ))


def seed():
    with SessionLocal() as s:
        roles = UserRoleRepository(s)
        users = UserRepository(s)
        depts = DepartmentRepository(s)
        clients = ClientRepository(s)
        pipelines = PipelineRepository(s)
        stages = PipelineStageRepository(s)
        atypes = ActivityTypeRepository(s)
        activities = ActivityRepository(s)
        deals = DealRepository(s)

        print("→ Roles")
        role_admin = _get_or_create_role(roles, "Администратор")
        role_head  = _get_or_create_role(roles, "Руководитель отдела")
        role_mgr   = _get_or_create_role(roles, "Менеджер")
        s.flush()

        print("→ Departments")
        dept_sales = _get_or_create_dept(depts, "Отдел продаж")
        dept_support = _get_or_create_dept(depts, "Отдел поддержки")
        s.flush()

        print("→ Users")
        admin = _get_or_create_user(
            users, name="Админ Админович", email="admin@example.com",
            phone="+79001112233", login="admin", password="admin123",
            role_id=role_admin.id, department_id=dept_sales.id,
        )
        head = _get_or_create_user(
            users, name="Пётр Руководителев", email="head@example.com",
            phone="+79004445566", login="head", password="head123",
            role_id=role_head.id, department_id=dept_sales.id,
        )
        manager = _get_or_create_user(
            users, name="Иван Менеджеров", email="manager@example.com",
            phone="+79007778899", login="manager", password="manager123",
            role_id=role_mgr.id, department_id=dept_sales.id,
        )
        if dept_sales.head_user_id != head.id:
            dept_sales.head_user_id = head.id
        s.flush()

        print("→ Clients")
        cl_a = _get_or_create_client(
            clients, name="ООО Ромашка", email="romashka@example.com",
            phone="+79001234567", responsible_user_id=manager.id,
        )
        cl_b = _get_or_create_client(
            clients, name="ИП Иванов", email="ivanov@example.com",
            phone="+79007654321", responsible_user_id=manager.id,
        )
        s.flush()

        print("→ Pipelines and stages")
        pipe = _get_or_create_pipeline(pipelines, "Основная воронка")
        s.flush()
        st_new = _get_or_create_stage(stages, name="Новая", pipeline_id=pipe.id)
        st_neg = _get_or_create_stage(stages, name="Переговоры", pipeline_id=pipe.id)
        st_won = _get_or_create_stage(stages, name="Успешно", pipeline_id=pipe.id)
        s.flush()

        print("→ Activity types")
        at_call  = _get_or_create_activity_type(atypes, "Звонок")
        at_meet  = _get_or_create_activity_type(atypes, "Встреча")
        at_email = _get_or_create_activity_type(atypes, "Email")
        s.flush()

        print("→ Deals")
        deal1 = _get_or_create_deal(
            deals, name="Поставка офисной мебели",
            main_client_id=cl_a.id, assigned_by_id=manager.id,
            created_by_id=admin.id, pipeline_id=pipe.id,
            pipeline_stage_id=st_neg.id, budget=500_000,
        )
        deal2 = _get_or_create_deal(
            deals, name="Разработка CRM",
            main_client_id=cl_b.id, assigned_by_id=manager.id,
            created_by_id=admin.id, pipeline_id=pipe.id,
            pipeline_stage_id=st_new.id, budget=1_200_000,
        )
        s.flush()
        if cl_b not in deal1.contact_clients:
            deal1.contact_clients.append(cl_b)
        if head not in deal1.supervised_by:
            deal1.supervised_by.append(head)
        s.flush()

        print("→ Activities")
        if not activities.list_by_deal(deal1.id):
            activities.add(Activity(
                deal_id=deal1.id, user_id=manager.id,
                activity_type_id=at_call.id, description="Обсудили сроки",
            ))
            activities.add(Activity(
                deal_id=deal1.id, user_id=manager.id,
                activity_type_id=at_meet.id, description="Встреча в офисе",
            ))
        if not activities.list_by_deal(deal2.id):
            activities.add(Activity(
                deal_id=deal2.id, user_id=manager.id,
                activity_type_id=at_email.id, description="Отправили КП",
            ))

        s.commit()
        print("\n✅ Seed done")
        print("Credentials: admin/admin123, head/head123, manager/manager123")


if __name__ == "__main__":
    seed()
