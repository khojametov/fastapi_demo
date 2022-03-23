
from backend import schemas
from backend.core.config import settings
from backend.crud import crud_user
from backend.db.database import SessionLocal


def init_db():
    db = SessionLocal()
    user = crud_user.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,

        )
        user = crud_user.user.create(db, obj=user_in)
