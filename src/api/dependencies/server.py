from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.services.key_service import KeyService
from src.api.services.server_service import ServerService
from src.api.services.server_user_service import ServerUserService
from src.common.database.connection import get_db_session
from src.common.repositories.server_repository import ServerRepository
from src.common.repositories.server_user_repository import ServerUserRepository
from src.common.services.cache_service import CacheService, get_cache_service


def get_key_service() -> KeyService:
    return KeyService()


def get_server_service(
    session: AsyncSession = Depends(get_db_session),
    key_service: KeyService = Depends(get_key_service),
    cache_service: CacheService = Depends(get_cache_service),
) -> ServerService:
    return ServerService(
        ServerRepository(session),
        key_service,
        ServerUserService(ServerUserRepository(session), cache_service),
        cache_service,
    )
