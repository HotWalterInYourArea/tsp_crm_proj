import uuid
from sqlalchemy.orm import Session

from db_service.repositories.client_repository import ClientRepository
from db_service.repositories.user_repository import UserRepository
from api_service.schemas.client_schema import ClientCreate, ClientUpdate, ClientRead


class ClientService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = ClientRepository(session)
        self.user_repo = UserRepository(session)

    def get(self, client_id: uuid.UUID) -> ClientRead:
        orm = self.repo.get(client_id)
        if orm is None:
            raise ValueError(f"Client {client_id} not found")
        return ClientRead.model_validate(orm)

    def list(self, **kw) -> list[ClientRead]:
        return [ClientRead.model_validate(o) for o in self.repo.list(**kw)]

    def create(self, payload: ClientCreate) -> ClientRead:
        if self.repo.get_by_email(payload.email):
            raise ValueError("Client email already exists")
        if self.user_repo.get(payload.responsible_user_id) is None:
            raise ValueError("Responsible user not found")
        orm = self.repo.add(self.repo.model(**payload.model_dump()))
        self.session.commit()
        self.session.refresh(orm)
        return ClientRead.model_validate(orm)

    def update(self, client_id: uuid.UUID, payload: ClientUpdate) -> ClientRead:
        orm = self.repo.get(client_id)
        if orm is None:
            raise ValueError(f"Client {client_id} not found")
        data = payload.model_dump(exclude_unset=True)
        if "email" in data and data["email"] != orm.email and self.repo.get_by_email(data["email"]):
            raise ValueError("Email already in use")
        if "responsible_user_id" in data and self.user_repo.get(data["responsible_user_id"]) is None:
            raise ValueError("Responsible user not found")
        for f, v in data.items():
            setattr(orm, f, v)
        self.session.commit()
        self.session.refresh(orm)
        return ClientRead.model_validate(orm)

    def delete(self, client_id: uuid.UUID) -> None:
        orm = self.repo.get(client_id)
        if orm is None:
            raise ValueError(f"Client {client_id} not found")
        if orm.deals:
            raise ValueError("Cannot delete client with linked deals")
        self.repo.delete(orm)
        self.session.commit()