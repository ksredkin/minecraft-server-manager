import asyncio
import json
from asyncio import Future
from typing import Any
from uuid import UUID, uuid4

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.api.exceptions.daemon import (
    DaemonDisconnectedError,
    InvalidDaemonResponseError,
)
from src.api.schemas.server import (
    FileCreate,
    FileCreateRequest,
    FileUpdate,
    FileUpdateRequest,
    FolderCreate,
    FolderUpdate,
)
from src.api.services.key_service import KeyService, get_key_service
from src.api.services.server_service import ServerService
from src.api.services.server_user_service import ServerUserService
from src.common.database.connection import session
from src.common.enums import (
    CacheResultStatus,
    DaemonRequestStatus,
)
from src.common.repositories.server_repository import ServerRepository
from src.common.repositories.server_user_repository import ServerUserRepository
from src.common.services.cache_service import CacheService, get_cache_service


class DaemonRequestResult:
    def __init__(
        self,
        status: DaemonRequestStatus,
        status_code: int = 200,
        error: str | None = None,
    ):
        self.status = status
        self.error = error
        self.status_code = status_code

    @property
    def success(self) -> bool:
        return self.status == DaemonRequestStatus.SUCCESS


class DaemonDataRequestResult(DaemonRequestResult):
    def __init__(
        self,
        status: DaemonRequestStatus,
        status_code: int = 200,
        data: Any = None,
        error: str | None = None,
    ):
        self.status = status
        self.error = error
        self.data = data
        self.status_code = status_code


class ConnectionManager:
    def __init__(
        self,
        key_service: KeyService,
        sessionmaker: async_sessionmaker[AsyncSession],
        cache_service: CacheService,
    ) -> None:
        self.connections: dict[int, WebSocket] = {}
        self.server_routes: dict[int, dict[str, str | int]] = {}
        self.pending_requests: dict[UUID, Future[dict[str, str | bool]]] = {}
        self.key_service = key_service
        self.sessionmaker = sessionmaker
        self.cache_service = cache_service

    async def _connect(self, connection: WebSocket) -> int:
        await connection.accept()
        connection_id = max(self.connections.keys(), default=0) + 1
        self.connections[connection_id] = connection
        return connection_id

    async def _get_server_id_by_daemon_key(
        self, daemon_key: str, server_service: ServerService
    ) -> int | None:
        cache_result = await self.cache_service.get_server_id_by_daemon_key(daemon_key)
        if cache_result.status == CacheResultStatus.NOT_FOUND:
            return None

        if cache_result.status == CacheResultStatus.FOUND:
            if isinstance(cache_result.value, int):
                server_id = cache_result.value
            else:
                server_id = None
        else:
            server_id = await server_service.resolve_server_id(daemon_key)
            if not server_id:
                await self.cache_service.set_server_id_by_daemon_key_not_found(
                    daemon_key
                )
                return None

            await self.cache_service.set_server_id_by_daemon_key(server_id, daemon_key)
        return server_id

    async def _recieve(self, connection_id: int) -> None:
        connection = self.connections.get(connection_id)
        if not connection:
            return

        need_to_disconnect = False
        while not need_to_disconnect:
            message = dict(await connection.receive_json())
            if not isinstance(message, dict):
                return

            match message.get("type"):
                case "register":
                    servers = message.get("servers")
                    if isinstance(servers, list):
                        registered = []
                        async with self.sessionmaker() as session:
                            server_service = ServerService(
                                ServerRepository(session),
                                self.key_service,
                                ServerUserService(
                                    ServerUserRepository(session), self.cache_service
                                ),
                                self.cache_service,
                            )
                            for server in servers:
                                if not isinstance(server, dict):
                                    continue

                                key = server.get("key")
                                if not isinstance(key, str):
                                    continue

                                server_id = await self._get_server_id_by_daemon_key(
                                    key, server_service
                                )

                                if not isinstance(server_id, int):
                                    continue

                                self.register_server_route(
                                    server_id, connection_id, key
                                )
                                registered.append(key)
                        if len(registered) == len(servers):
                            await connection.send_json(
                                {"type": "registered", "servers": servers}
                            )
                        elif len(registered) > 0:
                            await connection.send_json(
                                {
                                    "type": "registration_failed",
                                    "servers": [
                                        {**server, "error": "invalid_key"}
                                        for server in servers
                                        if server.get("key") not in registered
                                    ],
                                }
                            )
                        else:
                            await connection.send_json(
                                {
                                    "type": "registration_failed",
                                    "servers": [
                                        {**server, "error": "invalid_key"}
                                        for server in servers
                                    ],
                                }
                            )
                            need_to_disconnect = True
                case "request_completed" | "request_failed":
                    request_id = message.get("id")
                    if not isinstance(request_id, str):
                        continue

                    try:
                        request_uuid = UUID(request_id)
                    except ValueError:
                        continue

                    future = self.pending_requests.get(request_uuid)
                    if not future:
                        continue

                    future.set_result(message)
                case "status":
                    servers = message.get("servers")
                    if isinstance(servers, list):
                        async with self.sessionmaker() as session:
                            server_service = ServerService(
                                ServerRepository(session),
                                self.key_service,
                                ServerUserService(
                                    ServerUserRepository(session), self.cache_service
                                ),
                                self.cache_service,
                            )
                            for server in servers:
                                if not isinstance(server, dict):
                                    continue

                                key = server.get("key")
                                if not isinstance(key, str):
                                    continue

                                server_id = await self._get_server_id_by_daemon_key(
                                    key, server_service
                                )

                                if not isinstance(server_id, int):
                                    continue

                                status = server.get("status")
                                if not isinstance(status, dict):
                                    continue

                                logs = server.get("logs")
                                if not isinstance(logs, list):
                                    continue

                                metrics = server.get("metrics")
                                if not isinstance(metrics, dict):
                                    continue

                                await self.cache_service.publish_to_server_channel(
                                    server_id,
                                    json.dumps(
                                        {
                                            "status": status,
                                            "metrics": metrics,
                                            "logs": logs,
                                        }
                                    ),
                                )
        await connection.close()

    async def connect_and_subscribe_to_server_channel(
        self, websocket: WebSocket, server_id: int
    ) -> None:
        await websocket.accept()
        pubsub = await self.cache_service.create_server_pubsub(server_id)

        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    await websocket.send_text(message["data"])
        except asyncio.CancelledError:
            pass

    async def connect_and_recieve(self, websocket: WebSocket) -> None:
        connection_id: int | None = None
        try:
            connection_id = await self._connect(websocket)
            await self._recieve(connection_id)
        except WebSocketDisconnect:
            pass
        finally:
            if connection_id:
                await self.disconnect(connection_id)

    def register_server_route(
        self, server_id: int, connection_id: int, key: str
    ) -> None:
        self.server_routes[server_id] = {"connection_id": connection_id, "key": key}

    async def disconnect(self, connection_id: int) -> None:
        if connection_id in self.connections.keys():
            self.connections.pop(connection_id)

    async def send_message_to_server(
        self,
        server_id: int,
        message_type: str,
        **payload: str | bool | None,
    ) -> bool:
        if not (server_route := self.server_routes.get(server_id)):
            return False

        connection_id = server_route.get("connection_id")
        key = server_route.get("key")

        if not isinstance(connection_id, int) or not isinstance(key, str):
            return False

        if not (connection := self.connections.get(connection_id)):
            return False

        try:
            message = {"type": message_type, "key": key, **payload}
            await connection.send_json(message)
            return True
        except Exception:
            return False

    async def _send_request_and_wait(
        self, server_id: int, message_type: str, **payload: str | bool | None
    ) -> dict[str, str | bool]:
        request_id = uuid4()

        future = asyncio.get_running_loop().create_future()
        self.pending_requests[request_id] = future

        try:
            sent = await self.send_message_to_server(
                server_id, message_type, id=str(request_id), **payload
            )

            if not sent:
                raise DaemonDisconnectedError(
                    "Daemon is disconnected or an internal error occurred"
                )

            return await asyncio.wait_for(future, timeout=10)
        finally:
            self.pending_requests.pop(request_id, None)

    def _validate_response(self, result: dict[str, str | bool]) -> DaemonRequestStatus:
        if not result:
            raise InvalidDaemonResponseError("Internal server error")

        try:
            return DaemonRequestStatus(result.get("type"))
        except ValueError:
            raise InvalidDaemonResponseError("Internal server error")

    async def _execute_request(
        self,
        server_id: int,
        message_type: str,
        error: int = 409,
        **payload: str | bool | None,
    ) -> DaemonRequestResult:
        result = await self._send_request_and_wait(server_id, message_type, **payload)
        status = self._validate_response(result)

        if status == DaemonRequestStatus.SUCCESS:
            return DaemonRequestResult(
                status=DaemonRequestStatus.SUCCESS,
            )

        return DaemonRequestResult(
            status=DaemonRequestStatus.FAILED,
            status_code=error,
            error=str(result.get("error")),
        )

    async def _execute_data_request(
        self, server_id: int, message_type: str, error: int = 404, **payload: str | None
    ) -> DaemonDataRequestResult:
        result = await self._send_request_and_wait(server_id, message_type, **payload)
        status = self._validate_response(result)

        if status == DaemonRequestStatus.SUCCESS:
            return DaemonDataRequestResult(
                status=DaemonRequestStatus.SUCCESS, data=result.get("data")
            )

        return DaemonDataRequestResult(
            status=DaemonRequestStatus.FAILED,
            status_code=error,
            error=str(result.get("error")),
        )

    async def execute_server_action(
        self, server_id: int, action: str
    ) -> DaemonRequestResult:
        return await self._execute_request(server_id, "action", action=action)

    async def execute_server_command(
        self, server_id: int, command: str
    ) -> DaemonRequestResult:
        return await self._execute_request(server_id, "command", command=command)

    async def get_server_item(
        self, server_id: int, path: str | None = None
    ) -> DaemonDataRequestResult:
        return await self._execute_data_request(server_id, "files.get_item", path=path)

    async def create_server_file(
        self, server_id: int, file: FileCreate
    ) -> DaemonRequestResult:
        return await self._execute_request(
            server_id, "files.create_file", path=file.path, content=file.content
        )

    async def create_server_folder(
        self, server_id: int, folder: FolderCreate
    ) -> DaemonRequestResult:
        return await self._execute_request(
            server_id, "files.create_folder", path=folder.path
        )

    async def create_server_item(
        self, server_id: int, item: FileCreateRequest
    ) -> DaemonRequestResult:
        if isinstance(item, FileCreate):
            return await self.create_server_file(server_id, item)
        return await self.create_server_folder(server_id, item)

    async def update_server_file(
        self, server_id: int, file: FileUpdate
    ) -> DaemonRequestResult:
        return await self._execute_request(
            server_id,
            "files.update_file",
            path=file.path,
            new_path=file.new_path,
            new_content=file.new_content,
        )

    async def update_server_folder(
        self, server_id: int, folder: FolderUpdate
    ) -> DaemonRequestResult:
        return await self._execute_request(
            server_id, "files.update_folder", path=folder.path, new_path=folder.new_path
        )

    async def update_server_item(
        self, server_id: int, item: FileUpdateRequest
    ) -> DaemonRequestResult:
        if isinstance(item, FileUpdate):
            return await self.update_server_file(server_id, item)
        return await self.update_server_folder(server_id, item)

    async def delete_server_file(
        self, server_id: int, path: str
    ) -> DaemonRequestResult:
        return await self._execute_request(server_id, "files.delete_file", path=path)

    async def get_server_settings(self, server_id: int) -> DaemonDataRequestResult:
        return await self._execute_data_request(server_id, "properties.get")

    async def set_server_setting(
        self, server_id: int, property: str, new_value: str
    ) -> DaemonRequestResult:
        return await self._execute_request(
            server_id, "properties.set", property=property, new_value=new_value
        )

    async def get_server_eula(self, server_id: int) -> DaemonDataRequestResult:
        return await self._execute_data_request(server_id, "eula.get")

    async def set_server_eula(
        self, server_id: int, accept: bool
    ) -> DaemonRequestResult:
        return await self._execute_request(server_id, "eula.set", accept=accept)


connection_manager = ConnectionManager(get_key_service(), session, get_cache_service())


def get_connection_manager() -> ConnectionManager:
    return connection_manager
