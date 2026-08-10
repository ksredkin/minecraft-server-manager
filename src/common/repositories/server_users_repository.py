from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database.models import ServerUser


class ServerUsersRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_server_user(
        self, server_id: int, user_id: int, role: str, display_name: str
    ) -> ServerUser:
        server_user = ServerUser(
            server_id=server_id, user_id=user_id, role=role, display_name=display_name
        )
        self.session.add(server_user)
        await self.session.flush()
        return server_user
