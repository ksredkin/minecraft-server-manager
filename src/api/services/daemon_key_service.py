from src.common.repositories.daemon_key_repository import DaemonKeyRepository
from src.api.services.key_service import KeyService

class DaemonKeyService:
    def __init__(self, daemon_key_repository: DaemonKeyRepository, key_service: KeyService):
        self.daemon_key_repository = daemon_key_repository
        self.key_service = key_service

    async def create_daemon_key(self, server_id: int) -> str:
        key = self.key_service.create()
        key_hash = self.key_service.hash(key)
        await self.daemon_key_repository.create_daemon_key(server_id, key_hash)
        return key

    async def resolve_server_id(self, key: str) -> int|None:
        key_hash = self.key_service.hash(key)
        daemon_key = await self.daemon_key_repository.get_by_key_hash(key_hash)

        if not daemon_key:
            return None

        return daemon_key.server_id
