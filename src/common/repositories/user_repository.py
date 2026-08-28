from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database.models import ServerUser, User
from src.common.enums import ServerUserRole


class UserRespository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(
        self,
        login: str,
        password_hash: str,
        email: str | None = None,
        email_confirmed: bool = False,
    ) -> User:
        user = User(
            login=login,
            password_hash=password_hash,
            email=email,
            email_confirmed=email_confirmed,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_user_by_login(self, login: str) -> User | None:
        result = await self.session.execute(select(User).where(User.login == login))
        return result.scalar_one_or_none()

    async def get_server_owner(self, server_id: UUID) -> User | None:
        result = await self.session.execute(
            select(User)
            .join(ServerUser, ServerUser.user_id == User.id)
            .where(
                ServerUser.server_id == server_id,
                ServerUser.role == ServerUserRole.OWNER,
            )
        )
        return result.scalar_one_or_none()
