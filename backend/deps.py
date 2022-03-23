from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from backend import models
from backend.core.config import settings
from backend.crud import crud_user
from backend.db.database import SessionLocal
from backend.schemas import TokenPayload
from backend.security import ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> Optional[models.User]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=ALGORITHM)
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Couldn't validate credentials"
        )
    user = crud_user.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def get_current_active_user(current_user: models.User = Depends(get_current_user)) -> Optional[models.User]:
    if not crud_user.user.is_active(current_user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


def get_current_active_superuser(current_user: models.User = Depends(get_current_user)) -> Optional[models.User]:
    if not crud_user.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user doesn't have enough privileges"
        )
