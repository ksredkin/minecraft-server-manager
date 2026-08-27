from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.common.database.connection import get_db_session, session
from src.common.repositories.server_repository import ServerRepository
from src.common.repositories.server_user_repository import ServerUserRepository
from src.common.repositories.user_repository import UserRespository
from src.common.repositories.payment_repository import PaymentRepository


def get_async_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return session


def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> UserRespository:
    return UserRespository(session)


def get_server_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ServerRepository:
    return ServerRepository(session)


def get_server_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ServerUserRepository:
    return ServerUserRepository(session)


def get_payment_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PaymentRepository:
    return PaymentRepository(session)
