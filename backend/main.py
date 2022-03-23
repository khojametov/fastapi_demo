from typing import Any, Optional, Dict

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from backend import models, schemas, deps
from backend.crud import crud_user

from backend.initial_data import init_db
from backend.db.database import Base, engine

from backend.security import create_access_token

Base.metadata.create_all(bind=engine)
app = FastAPI()


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.post("/token")
def token(db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:
    user = crud_user.user.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect user or password")
    elif not crud_user.user.is_active(user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is inactive")

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer"
    }


@app.post("/login")
def login(
        *,
        db: Session = Depends(deps.get_db),
        user_in: schemas.UserCreate,
) -> Dict[str, str]:
    user = crud_user.user.authenticate(db, email=user_in.email, password=user_in.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect user or password")
    elif not crud_user.user.is_active(user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is inactive")

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer"
    }


@app.post("/users/", response_model=schemas.User)
def create_user(
        *,
        db: Session = Depends(deps.get_db),
        user_in: schemas.UserCreate,
        current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    user = crud_user.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    user = crud_user.user.create(db, obj=user_in)
    return user


@app.get("/users/me", response_model=schemas.User)
def read_user_me(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Optional[models.User]:
    return current_user
