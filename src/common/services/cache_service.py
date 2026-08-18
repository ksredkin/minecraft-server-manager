from uuid import UUID

from redis.asyncio import Redis
from redis.asyncio.client import PubSub

from src.common.enums import CacheResultStatus, ServerUserRole
from src.common.redis.connection import r
from src.common.utils.logger import Logger

logger = Logger(__name__)


class CacheResult:
    def __init__(
        self, status: CacheResultStatus, value: int | ServerUserRole | None = None
    ) -> None:
        self.status = status
        self.value = value


class CacheService:
    NOT_FOUND = "NOT_FOUND"

    def __init__(self, redis: Redis = r) -> None:
        self.r = redis

    async def _get(self, prefix: str, key: str, postfix: str = "") -> str | None:
        result = await self.r.get(f"{prefix}:{key}:{postfix}")
        logger.debug(
            f"Из кэша по ключу {f'{prefix}:{key}:{postfix}'} получено значение: {result}"  # type: ignore
        )
        return result  # type: ignore

    async def _set(
        self,
        prefix: str,
        key: str,
        value: str,
        postfix: str = "",
        expire: int | None = None,
    ) -> None:
        logger.debug(
            f"По ключу {f'{prefix}:{key}:{postfix}'} в кэше установлено новое значение: {value} (expire {f'через {expire} секунд' if expire else 'не установлен'})"
        )
        await self.r.set(f"{prefix}:{key}:{postfix}", value, ex=expire)

    def _create_pubsub(self) -> PubSub:
        return self.r.pubsub()

    async def _publish_to_channel(self, channel: str, message: str) -> None:
        await self.r.publish(channel, message)

    async def create_server_pubsub(self, server_id: int) -> PubSub:
        pubsub = self._create_pubsub()
        await pubsub.subscribe(f"logs:server:{str(server_id)}")
        return pubsub

    async def publish_to_server_channel(self, server_id: int, message: str) -> None:
        await self._publish_to_channel(f"logs:server:{str(server_id)}", message)

    async def set_server_id(self, server_id: int, server_uuid: UUID) -> None:
        await self._set("server", str(server_uuid), str(server_id))

    async def set_server_not_found(self, server_uuid: UUID, expire: int = 3600) -> None:
        await self._set("server", str(server_uuid), self.NOT_FOUND, expire=expire)

    async def get_server_id(self, server_uuid: UUID) -> CacheResult:
        value = await self._get("server", str(server_uuid))

        if value == self.NOT_FOUND:
            return CacheResult(CacheResultStatus.NOT_FOUND)

        if not value:
            return CacheResult(CacheResultStatus.MISS)

        return CacheResult(CacheResultStatus.FOUND, int(value))

    async def set_server_user_role(
        self, user_id: int, server_id: int, role: ServerUserRole, expire: int = 3600
    ) -> None:
        await self._set(
            "server_user", f"{user_id}:{server_id}", str(role.value), "role", expire
        )

    async def get_server_user_role(self, user_id: int, server_id: int) -> CacheResult:
        value = await self._get("server_user", f"{user_id}:{server_id}", "role")

        if value == self.NOT_FOUND:
            return CacheResult(CacheResultStatus.NOT_FOUND)

        if not value:
            return CacheResult(CacheResultStatus.MISS)

        return CacheResult(CacheResultStatus.FOUND, ServerUserRole(value))

    async def set_server_user_role_not_found(
        self, user_id: int, server_id: int, expire: int = 3600
    ) -> None:
        await self._set(
            "server_user", f"{user_id}:{server_id}", self.NOT_FOUND, "role", expire
        )

    async def set_server_id_by_daemon_key(
        self, server_id: int, daemon_key: str, expire: int = 3600
    ) -> None:
        await self._set("daemon_key", daemon_key, str(server_id), expire=expire)

    async def set_server_id_by_daemon_key_not_found(
        self, daemon_key: str, expire: int = 3600
    ) -> None:
        await self._set("daemon_key", daemon_key, self.NOT_FOUND, expire=expire)

    async def get_server_id_by_daemon_key(self, daemon_key: str) -> CacheResult:
        value = await self._get("daemon_key", daemon_key)

        if value == self.NOT_FOUND:
            return CacheResult(CacheResultStatus.NOT_FOUND)

        if not value:
            return CacheResult(CacheResultStatus.MISS)

        return CacheResult(CacheResultStatus.FOUND, int(value))


cache_service = CacheService()


def get_cache_service() -> CacheService:
    return cache_service
