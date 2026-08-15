from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database.models import Server, ServerUser


class ServerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_server(self, uuid: UUID, daemon_key_hash: str) -> Server:
        server = Server(uuid=uuid, daemon_key_hash=daemon_key_hash)
        self.session.add(server)
        await self.session.flush()
        return server

    async def get_by_id(self, server_id: int) -> Server | None:
        result = await self.session.execute(
            select(Server).where(Server.id == server_id)
        )
        return result.scalar_one_or_none()

    async def get_by_uuid(self, uuid: UUID) -> Server | None:
        result = await self.session.execute(select(Server).where(Server.uuid == uuid))
        return result.scalar_one_or_none()

    async def get_by_daemon_key_hash(self, daemon_key_hash: str) -> Server | None:
        result = await self.session.execute(
            select(Server).where(Server.daemon_key_hash == daemon_key_hash)
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int) -> list[dict[str, str | datetime | UUID]]:
        result = await self.session.execute(
            select(
                Server.uuid, Server.created_at, ServerUser.display_name, ServerUser.role
            )
            .join(Server.server_users)
            .where(ServerUser.user_id == user_id)
        )
        return [dict(row) for row in result.mappings().all()]

    async def delete_by_uuid(self, uuid: UUID) -> Server | None:
        result = await self.session.execute(
            delete(Server).where(Server.uuid == uuid).returning(Server)
        )
        return result.scalar_one_or_none()
