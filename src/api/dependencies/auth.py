from fastapi import Depends, WebSocket, WebSocketException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.api.dependencies.database import get_user_repository
from src.api.services.auth_service import AuthService
from src.api.services.jwt_service import JwtService
from src.api.services.password_service import PasswordService
from src.api.services.user_service import UserService
from src.common.core.config import settings, secrets
from src.common.repositories.user_repository import UserRespository
from src.common.repositories.subscription_repository import SubscriptionRepository
from src.common.repositories.payment_repository import PaymentRepository
from src.api.services.subscription_service import SubscriptionService
from src.api.services.payment_service import PaymentService
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.database.connection import get_db_session
from src.api.api_clients.payments.interface import PaymentProvider
from src.api.dependencies.billing import get_yoocassa_provider


def get_password_service() -> PasswordService:
    return PasswordService()


def get_user_service(
    session: AsyncSession = Depends(get_db_session), 
    password_service: PasswordService = Depends(get_password_service),
    payment_provider: PaymentProvider = Depends(get_yoocassa_provider),
) -> UserService:
    return UserService(UserRespository(session), password_service, SubscriptionService(SubscriptionRepository(session), PaymentService(PaymentRepository(session), payment_provider)))


def get_jwt_service() -> JwtService:
    if secrets.get("jwt_secret_key") is None:
        raise RuntimeError("JWT_SECRET_KEY is not configured")

    return JwtService(secrets.get("jwt_secret_key"), settings.jwt_algorithm)


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


def get_current_user_id_ws(
    websocket: WebSocket,
    jwt_service: JwtService = Depends(get_jwt_service),
) -> int:
    authorization = websocket.headers.get("authorization")

    if not authorization:
        raise WebSocketException(code=1008)

    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token:
        raise WebSocketException(code=1008)

    try:
        return jwt_service.decode(token)
    except Exception:
        raise WebSocketException(code=1008)
