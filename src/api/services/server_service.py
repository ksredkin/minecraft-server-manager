from src.common.database.models import Server
from src.common.repositories.server_repository import ServerRepository
from uuid import uuid4, UUID
from src.api.services.key_service import KeyService
from src.api.schemas.server import ServerCreated
from datetime import datetime
from src.api.services.server_user_service import ServerUserService

class ServerService:
    def __init__(self, server_repository: ServerRepository, key_service: KeyService, server_user_service: ServerUserService):
        self.server_repository = server_repository
        self.key_service = key_service
        self.server_user_service = server_user_service

    async def create_server(self, user_id: int, display_name: str) -> ServerCreated:
        daemon_key = self.key_service.create()
        server = await self.server_repository.create_server(uuid4(), self.key_service.hash(daemon_key))
        await self.server_user_service.create_server_user(server.id, user_id, display_name or str(server.uuid), "owner")
        return ServerCreated(id=server.id, uuid=server.uuid, daemon_key=daemon_key, created_at=server.created_at)

    async def get_by_uuid(self, uuid: str) -> Server|None:
        return await self.server_repository.get_by_uuid(UUID(uuid))

    async def resolve_server_id(self, daemon_key: str) -> int|None:
        key_hash = self.key_service.hash(daemon_key)
        server = await self.server_repository.get_by_daemon_key_hash(key_hash)
    
        if not server:
            return None
    
        return server.id

    async def get_by_user(self, user_id: int) -> list[dict[str, str|datetime|UUID]]:
        return await self.server_repository.get_by_user(user_id)

    async def delete_for_user(self, user_id: int, uuid: UUID) -> Server|None:
        server = await self.server_repository.get_by_uuid(uuid)
        if not server:
            return None

        server_user = await self.server_user_service.get_by_user_and_server(user_id, server.id)
        if not server_user or not self.server_user_service.is_owner(server_user):
            return None

        return await self.server_repository.delete_by_uuid(uuid)

