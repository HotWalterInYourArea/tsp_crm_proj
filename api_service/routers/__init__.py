from api_service.routers.auth_router import router as auth_router
from api_service.routers.user_router import router as users_router
from api_service.routers.role_router import router as roles_router
from api_service.routers.department_router import router as departments_router
from api_service.routers.client_router import router as clients_router
from api_service.routers.pipeline_router import router as pipelines_router
from api_service.routers.activity_type_router import router as activity_types_router
from api_service.routers.activity_router import router as activities_router
from api_service.routers.deal_router import router as deals_router

all_routers = [
    auth_router,
    users_router,
    roles_router,
    departments_router,
    clients_router,
    pipelines_router,
    activity_types_router,
    activities_router,
    deals_router,
]