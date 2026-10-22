import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from api_service.core.security import decode_token
from db_service.session import get_db
from db_service.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id = uuid.UUID(decode_token(token))
    except (JWTError, ValueError):
        raise credentials_exc

    user = db.get(User, user_id)
    if user is None:
        raise credentials_exc
    return user


def require_admin(current: User = Depends(get_current_user)) -> User:
    if not current.role or current.role.name != "Администратор":
        raise HTTPException(status_code=403, detail="Admin role required")
    return current

def require_admin_or_head(current: User = Depends(get_current_user)) -> User:
    is_admin = current.role and current.role.name == "Администратор"
    is_head = bool(current.supervised_departments)
    
    if not (is_admin or is_head):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Department Head privileges required",
        )
    return current
                     