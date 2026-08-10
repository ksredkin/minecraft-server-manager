from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database.models import DaemonKey


class DaemonKeysRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_daemon_key(self, server_id: int, key_hash: str) -> DaemonKey:
        daemon_key = DaemonKey(server_id=server_id, key_hash=key_hash)
        self.session.add(daemon_key)
        await self.session.flush()
        return daemon_key
