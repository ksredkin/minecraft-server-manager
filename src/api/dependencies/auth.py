from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.services.auth_service import AuthService
from src.api.services.jwt_service import JwtService
from src.api.services.password_service import PasswordService
from src.api.services.user_service import UserService
from src.common.core.config import settings
from src.common.database.connection import get_db_session
from src.common.repositories.user_repository import UserRespository


def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> UserRespository:
    return UserRespository(session)


def get_password_service() -> PasswordService:
    return PasswordService()


def get_user_service(
    user_repository: UserRespository = Depends(get_user_repository),
    password_service: PasswordService = Depends(get_password_service),
) -> UserService:
    return UserService(user_repository, password_service)


def get_jwt_service() -> JwtService:
    if settings.jwt_secret_key is None:
        raise RuntimeError("JWT_SECRET_KEY is not configured")

    return JwtService(settings.jwt_secret_key, settings.jwt_algorithm)


def get_auth_service(
    user_service: UserService = Depends(get_user_service),
    jwt_service: JwtService = Depends(get_jwt_service),
) -> AuthService:
    return AuthService(user_service, jwt_service)


security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_service: JwtService = Depends(get_jwt_service),
) -> int:
    return jwt_service.decode(credentials.credentials)
