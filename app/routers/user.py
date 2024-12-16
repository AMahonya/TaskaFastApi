from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.protection import get_password_hash, create_access_token, get_user_by_token, verify_password

router = APIRouter(tags=["user"])


@router.post("/register/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Создает нового пользователя.

    Args:
        user (UserCreate): Данные для создания пользователя.
        db (Session, optional): Сессия базы данных. Defaults to Depends(get_db).

    Returns:
        UserResponse: Созданный пользователь.
    """
    db_user = User(username=user.username, email=user.email, hashed_password=get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/api/v1/login/")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    """
    Аутентифицирует пользователя и возвращает токен доступа.

    Args:
        form_data (Annotated[OAuth2PasswordRequestForm, Depends]): Данные для аутентификации.
        db (Session, optional): Сессия базы данных. Defaults to Depends(get_db).

    Returns:
        dict: Токен доступа и его тип.

    Raises:
        HTTPException: Если данные не верны.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    jwt_token = create_access_token({"sub": form_data.username})
    return {"access_token": jwt_token, "token_type": "bearer"}


@router.get("/about_me/", response_model=UserResponse)
def read_user(db: Session = Depends(get_db), username: str = Depends(get_user_by_token)):
    """
    Возвращает информацию о текущем пользователе.

    Args:
        db (Session, optional): Сессия базы данных. Defaults to Depends(get_db).
        username (str, optional): Имя пользователя из токена. Defaults to Depends(get_user_by_token).

    Returns:
        UserResponse: Информация о пользователе.

    Raises:
        HTTPException: Если пользователь не найден.
    """
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
