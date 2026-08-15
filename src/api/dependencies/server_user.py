from fastapi import Depends

from src.api.dependencies.database import get_server_user_repository
from src.api.services.server_user_service import ServerUserService
from src.common.repositories.server_user_repository import ServerUserRepository
from src.common.services.cache_service import CacheService, get_cache_service


def get_server_user_service(
    server_repository: ServerUserRepository = Depends(get_server_user_repository),
    cache_service: CacheService = Depends(get_cache_service),
) -> ServerUserService:
    return ServerUserService(server_repository, cache_service)
