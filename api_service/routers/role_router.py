import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api_service.core.deps import require_admin
from db_service.session import get_db
from api_service.services.user_service import UserRoleService
from api_service.schemas.user_schema import UserRoleCreate, UserRoleRead, UserRoleUpdate

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=list[UserRoleRead], dependencies=[Depends(require_admin)])
def list_roles(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return UserRoleService(db).list(offset=offset, limit=limit)


@router.post("", response_model=UserRoleRead, status_code=201, dependencies=[Depends(require_admin)])
def create_role(payload: UserRoleCreate, db: Session = Depends(get_db)):
    try:
        return UserRoleService(db).create(payload)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.patch("/{role_id}", response_model=UserRoleRead, dependencies=[Depends(require_admin)])
def update_role(role_id: uuid.UUID, payload: UserRoleUpdate, db: Session = Depends(get_db)):
    try:
        return UserRoleService(db).update(role_id, payload)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.delete("/{role_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_role(role_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        UserRoleService(db).delete(role_id)
    except ValueError as e:
        raise HTTPException(400, str(e))