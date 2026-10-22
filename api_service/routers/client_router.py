import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api_service.core.deps import get_current_user
from db_service.session import get_db
from api_service.services.client_service import ClientService
from api_service.schemas.client_schema import ClientCreate, ClientRead, ClientUpdate

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("", response_model=list[ClientRead], dependencies=[Depends(get_current_user)])
def list_clients(
    offset: int = 0, limit: int = 100,
    responsible_user_id: uuid.UUID | None = None,
    name_contains: str | None = None,
    db: Session = Depends(get_db),
):
    return ClientService(db).list(
        offset=offset, limit=limit,
        responsible_user_id=responsible_user_id,
        name_contains=name_contains,
    )


@router.get("/{client_id}", response_model=ClientRead, dependencies=[Depends(get_current_user)])
def get_client(client_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        return ClientService(db).get(client_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("", response_model=ClientRead, status_code=201, dependencies=[Depends(get_current_user)])
def create_client(payload: ClientCreate, db: Session = Depends(get_db)):
    try:
        return ClientService(db).create(payload)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.patch("/{client_id}", response_model=ClientRead, dependencies=[Depends(get_current_user)])
def update_client(client_id: uuid.UUID, payload: ClientUpdate, db: Session = Depends(get_db)):
    try:
        return ClientService(db).update(client_id, payload)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.delete("/{client_id}", status_code=204, dependencies=[Depends(get_current_user)])
def delete_client(client_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        ClientService(db).delete(client_id)
    except ValueError as e:
        raise HTTPException(400, str(e))