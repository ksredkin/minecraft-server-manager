from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database.models import Server
from sqlalchemy import select
from uuid import UUID



class ServerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_server(self, uuid: str) -> Server:
        server = Server(uuid=uuid)
        self.session.add(server)
        await self.session.flush()
        return server

    async def get_by_uuid(self, uuid: UUID) -> Server|None:
        result = await self.session.execute(select(Server).where(Server.uuid == uuid))
        return result.scalar_one_or_none()
