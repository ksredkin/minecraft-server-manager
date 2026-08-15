from src.common.database.models import ServerUser
from src.common.enums import CacheResultStatus, ServerUserRole
from src.common.repositories.server_user_repository import ServerUserRepository
from src.common.services.cache_service import CacheService


class ServerUserService:
    def __init__(
        self, server_user_repository: ServerUserRepository, cache_service: CacheService
    ):
        self.server_user_repository = server_user_repository
        self.cache_service = cache_service

    async def create_server_user(
        self,
        server_id: int,
        user_id: int,
        display_name: str,
        role: ServerUserRole = ServerUserRole.VIEWER,
    ) -> ServerUser | None:
        existing_server_user = await self.server_user_repository.get_by_user_and_server(
            user_id, server_id
        )

        if existing_server_user:
            return None

        await self.cache_service.set_server_user_role(user_id, server_id, role)
        return await self.server_user_repository.create_server_user(
            server_id, user_id, role, display_name
        )

    async def get_by_user_and_server(
        self, user_id: int, server_id: int
    ) -> ServerUser | None:
        server_user = await self.server_user_repository.get_by_user_and_server(
            user_id, server_id
        )

        if not server_user:
            await self.cache_service.set_server_user_role_not_found(user_id, server_id)
            return None

        await self.cache_service.set_server_user_role(
            user_id, server_id, server_user.role
        )
        return server_user

    async def get_by_user(self, user_id: int) -> list[ServerUser]:
        return await self.server_user_repository.get_by_user(user_id)

    async def is_owner(self, user_id: int, server_id: int) -> bool:
        cache_result = await self.cache_service.get_server_user_role(user_id, server_id)
        if cache_result.status == CacheResultStatus.FOUND:
            return cache_result.value == ServerUserRole.OWNER
        elif cache_result.status == CacheResultStatus.NOT_FOUND:
            return False

        server_user = await self.get_by_user_and_server(user_id, server_id)
        if not server_user:
            await self.cache_service.set_server_user_role_not_found(user_id, server_id)
            return False

        return server_user.role == ServerUserRole.OWNER
