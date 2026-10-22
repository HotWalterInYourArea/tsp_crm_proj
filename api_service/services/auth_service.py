from sqlalchemy.orm import Session

from api_service.core.security import verify_password, create_access_token
from db_service.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)

    def authenticate(self, login: str, password: str) -> tuple[str, str] | None:
        user = self.user_repo.get_by_login(login)
        if not user or not verify_password(password, user.hashed_password):
            return None
        token = create_access_token(subject = user.id)
        return token, "bearer"