from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database.models import DaemonKey
from sqlalchemy import select


class DaemonKeyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_daemon_key(self, server_id: int, key_hash: str) -> DaemonKey:
        daemon_key = DaemonKey(server_id=server_id, key_hash=key_hash)
        self.session.add(daemon_key)
        await self.session.flush()
        return daemon_key

    async def get_by_key_hash(self, key_hash: str) -> DaemonKey|None:
        result = await self.session.execute(select(DaemonKey).where(DaemonKey.key_hash == key_hash))
        return result.scalar_one_or_none()
