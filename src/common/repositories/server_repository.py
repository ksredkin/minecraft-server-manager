from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database.models import Server


class UserRespository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_server(self, uuid: str) -> Server:
        server = Server(uuid=uuid)
        self.session.add(server)
        await self.session.flush()
        return server
