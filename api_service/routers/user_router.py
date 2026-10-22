import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api_service.core.deps import get_current_user, require_admin, require_admin_or_head
from db_service.session import get_db
from api_service.services.user_service import UserService
from api_service.schemas.user_schema import UserCreate, UserRead, UserUpdate

from db_service.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def me(current=Depends(get_current_user)):
    return current


@router.get("", response_model=list[UserRead], dependencies=[Depends(get_current_user)])
def list_users(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return UserService(db).list(offset=offset, limit=limit)


@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(get_current_user)])
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        return UserService(db).get(user_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("", response_model=UserRead, status_code=201)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_head),
):
    service = UserService(db)

    try:
        if current_user.role.name == "Администратор":
            return service.create_user(payload)
        else:
            return service.create_user_by_head(payload, current_user)

    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{user_id}", response_model=UserRead, dependencies=[Depends(require_admin)])
def update_user(user_id: uuid.UUID, payload: UserUpdate, db: Session = Depends(get_db)):
    try:
        return UserService(db).update(user_id, payload)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: uuid.UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_head) 
):
    service = UserService(db)

    if current_user.role.name == "Администратор":
        try:
            service.delete(user_id)
        except ValueError as e:
            raise HTTPException(400, str(e))
    else:
        try:
            service.delete_user_by_head(user_id, current_user)
        except PermissionError as e:
            raise HTTPException(403, str(e))
        except ValueError as e:
            raise HTTPException(400, str(e))