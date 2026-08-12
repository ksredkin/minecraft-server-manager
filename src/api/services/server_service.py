from src.common.database.models import Server
from src.common.repositories.server_repository import ServerRepository
from uuid import uuid4, UUID

class ServerService:
    def __init__(self, server_repository: ServerRepository):
        self.server_repository = server_repository

    async def create_server(self) -> Server:
        return await self.server_repository.create_server(uuid4())

    async def get_by_uuid(self, uuid: str) -> Server|None:
        server = await self.server_repository.get_by_uuid(UUID(uuid))

        if not server:
            return None

        return server
