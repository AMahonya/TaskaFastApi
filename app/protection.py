from datetime import datetime, timedelta
from typing import Any

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login/")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password) -> bool:
    """
    Проверяет, соответствует ли открытый пароль хешированному паролю.

    Args:
        plain_password (str): Открытый пароль для проверки.
        hashed_password (str): Хешированный пароль для сравнения.

    Returns:
        bool: True, если пароли совпадают, False в противном случае.
    """
    return pwd_context.verify(plain_password + settings.SALT, hashed_password)


def get_password_hash(password) -> Any:
    """
    Хеширует пароль с использованием bcrypt.

    Args:
        password (str): Пароль для хеширования.

    Returns:
        str: Хешированный пароль.
    """
    return pwd_context.hash(password + settings.SALT)


def create_access_token(data: dict) -> str:
    """
    Создает JWT токен доступа.

    Args:
        data (dict): Словарь с данными для включения в токен.

    Returns:
        str: Сформированный JWT токен.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Декодирует и проверяет JWT токен доступа.

    Args:
        token (str, optional): Токен доступа, получаемый из заголовка Authorization.

    Returns:
        dict: Декодированная полезная нагрузка токена.

    Raises:
        HTTPException: Если токен недействителен.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_by_token(payload: dict = Depends(decode_access_token)) -> str:
    """
    Извлекает user_id из токена доступа.

    Args:
        payload (dict, optional): Полезная нагрузка токена, получаемая от decode_access_token.

    Returns:
        str: Идентификатор пользователя (обычно это значение ключа 'sub').
    """
    return payload.get("sub")
