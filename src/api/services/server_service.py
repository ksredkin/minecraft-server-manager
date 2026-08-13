from src.common.database.models import Server
from src.common.repositories.server_repository import ServerRepository
from uuid import uuid4, UUID
from src.api.services.key_service import KeyService
from src.api.schemas.server import ServerCreated
from datetime import datetime

class ServerService:
    def __init__(self, server_repository: ServerRepository, key_service: KeyService):
        self.server_repository = server_repository
        self.key_service = key_service

    async def create_server(self) -> ServerCreated:
        daemon_key = self.key_service.create()
        server = await self.server_repository.create_server(uuid4(), self.key_service.hash(daemon_key))
        return ServerCreated(id=server.id, uuid=server.uuid, daemon_key=daemon_key)

    async def get_by_uuid(self, uuid: str) -> Server|None:
        server = await self.server_repository.get_by_uuid(UUID(uuid))

        if not server:
            return None

        return server

    async def resolve_server_id(self, daemon_key: str) -> int|None:
        key_hash = self.key_service.hash(daemon_key)
        server = await self.server_repository.get_by_daemon_key_hash(key_hash)
    
        if not server:
            return None
    
        return server.id

    async def get_by_user(self, user_id: int) -> list[dict[str, str|datetime|UUID]]:
        return await self.server_repository.get_by_user(user_id)
