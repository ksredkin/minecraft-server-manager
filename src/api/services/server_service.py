from datetime import datetime
from uuid import UUID, uuid4

from src.api.schemas.server import ServerCreated
from src.api.services.key_service import KeyService
from src.api.services.server_user_service import ServerUserService
from src.common.database.models import Server
from src.common.enums import CacheResultStatus, ServerUserRole
from src.common.repositories.server_repository import ServerRepository
from src.common.services.cache_service import CacheResult, CacheService


class ServerService:
    def __init__(
        self,
        server_repository: ServerRepository,
        key_service: KeyService,
        server_user_service: ServerUserService,
        cache_service: CacheService,
    ):
        self.server_repository = server_repository
        self.key_service = key_service
        self.server_user_service = server_user_service
        self.cache_service = cache_service

    async def create_server(
        self, user_id: int, display_name: str | None = None
    ) -> ServerCreated:
        daemon_key = self.key_service.create()
        server = await self.server_repository.create_server(
            uuid4(), self.key_service.hash(daemon_key)
        )
        await self.server_user_service.create_server_user(
            server.id, user_id, display_name or str(server.uuid), ServerUserRole.OWNER
        )
        await self.cache_service.set_server_id(server.id, server.uuid)
        return ServerCreated(
            id=server.id,
            uuid=server.uuid,
            daemon_key=daemon_key,
            created_at=server.created_at,
        )

    async def get_server_id(self, server_uuid: UUID) -> int | None:
        cache_result: CacheResult = await self.cache_service.get_server_id(server_uuid)

        if cache_result.status == CacheResultStatus.NOT_FOUND:
            return None

        if cache_result.status == CacheResultStatus.FOUND:
            return cache_result.value  # type: ignore

        server = await self.server_repository.get_by_uuid(server_uuid)

        if not server:
            await self.cache_service.set_server_not_found(server_uuid)
            return None

        await self.cache_service.set_server_id(server.id, server_uuid)
        return server.id

    async def get_by_uuid(self, server_uuid: UUID) -> Server | None:
        server_id = await self.get_server_id(server_uuid)

        if server_id is None:
            return None

        return await self.server_repository.get_by_id(server_id)

    async def resolve_server_id(self, daemon_key: str) -> int | None:
        key_hash = self.key_service.hash(daemon_key)
        server = await self.server_repository.get_by_daemon_key_hash(key_hash)

        if not server:
            return None

        await self.cache_service.set_server_id(server.id, server.uuid)
        return server.id

    async def get_by_user(self, user_id: int) -> list[dict[str, str | datetime | UUID]]:
        return await self.server_repository.get_by_user(user_id)

    async def delete_for_user(self, user_id: int, uuid: UUID) -> Server | None:
        server = await self.get_by_uuid(uuid)
        if not server:
            return None

        if not await self.is_owner(user_id, server.id):
            return None

        return await self.server_repository.delete_by_uuid(uuid)

    async def is_owner(self, user_id: int, server_id: int) -> bool:
        role_cache_result = await self.cache_service.get_server_user_role(
            user_id, server_id
        )

        if role_cache_result.status == CacheResultStatus.FOUND:
            return role_cache_result.value == ServerUserRole.OWNER

        if role_cache_result.status == CacheResultStatus.NOT_FOUND:
            return False

        server_user = await self.server_user_service.get_by_user_and_server(
            user_id, server_id
        )
        if not server_user:
            await self.cache_service.set_server_user_role_not_found(user_id, server_id)
            return False

        is_owner = server_user.role == ServerUserRole.OWNER

        await self.cache_service.set_server_user_role(
            user_id, server_id, server_user.role
        )
        return is_owner
