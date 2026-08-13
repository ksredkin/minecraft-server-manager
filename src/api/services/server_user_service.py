from src.common.database.models import ServerUser
from src.common.repositories.server_user_repository import ServerUserRepository

class ServerUserService:
    def __init__(self, server_user_repository: ServerUserRepository):
        self.server_user_repository = server_user_repository

    async def create_server_user(self, server_id: int, user_id: int, display_name: str, role: str = "viewer") -> ServerUser|None:
        existing_server_user = await self.server_user_repository.get_by_user_and_server(user_id, server_id)

        if existing_server_user:
            return None

        return await self.server_user_repository.create_server_user(server_id, user_id, role, display_name)

    async def get_by_user_and_server(self, user_id: int, server_id: int) -> ServerUser|None:
        server_user = await self.server_user_repository.get_by_user_and_server(user_id, server_id)

        if not server_user:
            return None

        return server_user

    async def get_by_user(self, user_id: int) -> list[ServerUser]:
        return await self.server_user_repository.get_by_user(user_id)

    async def is_owner(self, server_user: ServerUser) -> bool:
        return server_user.role == "owner"
