import uuid
from jose import jwt, JWTError
from fastapi import HTTPException, status

from .config import settings


def decode_user_id(token: str) -> uuid.UUID:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        sub = payload.get("sub") or payload.get("user_id")
        if not sub:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "no sub in token")
        return uuid.UUID(str(sub))
    except (JWTError, ValueError) as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"invalid token: {e}")


def resolve_user_id(token: str | None, user_id_query: str | None) -> uuid.UUID:
    if token:
        return decode_user_id(token)
    if settings.allow_query_token and user_id_query:
        try:
            return uuid.UUID(user_id_query)
        except ValueError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "bad user_id")
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing credentials")