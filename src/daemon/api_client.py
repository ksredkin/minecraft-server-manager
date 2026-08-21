import asyncio
import json
from typing import Any
from uuid import UUID

from websockets import ClientConnection, connect
from websockets.exceptions import ConnectionClosed, InvalidMessage

from src.common.utils.logger import Logger
from src.daemon.exceptions.api_client import NoValidDaemonKeysError
from src.daemon.exceptions.config import InvalidConfigError
from src.daemon.exceptions.server import (
    ServerIsAlreadyRunningError,
    ServerIsNotRunningError,
    ServerStopTimeoutError,
)
from src.daemon.server import Server
from src.daemon.services.file_service import FileItem, FileService, FolderItem
from src.daemon.services.metrics_service import MetricsService
from src.daemon.services.properties_service import PropertiesService

logger = Logger(__name__)


class APIClient:
    def __init__(
        self,
        api_host: str,
        api_port: int,
        servers: list[Server],
        metrics_service: MetricsService,
        file_service: FileService,
        properties_service: PropertiesService,
    ):
        if not api_host:
            raise InvalidConfigError('Missing "api_host" in daemon settings.')

        if not api_port:
            raise InvalidConfigError('Missing "api_port" in daemon settings.')

        self._api_uri = f"ws://{api_host}:{api_port}/ws/daemon"

        self._servers_by_key: dict[str, Server] = {}
        for server in servers:
            if not isinstance(server.key, str):
                raise InvalidConfigError('Daemon setting "key" must be a string')
            self._servers_by_key[server.key] = server

        self.metrics_service = metrics_service
        self.file_service = file_service
        self.properties_service = properties_service

    async def _send_json(self, websocket: ClientConnection, data: Any) -> None:
        await websocket.send(json.dumps(data), text=True)

    async def _request_failed(
        self, websocket: ClientConnection, request_id: UUID, error: str | None = None
    ) -> None:
        message = {"id": request_id, "type": "request_failed"}
        if error is not None:
            message["error"] = error
        await self._send_json(websocket, message)

    async def _request_completed(
        self, websocket: ClientConnection, request_id: UUID, data: Any | None = None
    ) -> None:
        message = {"id": request_id, "type": "request_completed"}
        if data is not None:
            message["data"] = data
        await self._send_json(websocket, message)

    async def _recieve_commands(self, websocket: ClientConnection) -> None:
        while True:
            message: dict[str, str | list[dict[str, str]]] = json.loads(
                await websocket.recv()
            )
            if not isinstance(message, dict):
                continue

            message_type = message.get("type")
            match message_type:
                case (
                    "action"
                    | "command"
                    | "files.get_item"
                    | "files.create_file"
                    | "files.create_folder"
                    | "files.update_file"
                    | "files.update_folder"
                    | "files.delete"
                    | "properties.get"
                    | "properties.set"
                ):
                    key = message.get("key")
                    if not isinstance(key, str):
                        continue

                    server = self._servers_by_key.get(key)
                    if not isinstance(server, Server):
                        continue

                    request_id_str = message.get("id")
                    if not isinstance(request_id_str, str):
                        continue

                    try:
                        request_id = UUID(request_id_str)
                    except ValueError:
                        continue

                    match message_type:
                        case "action":
                            action = message.get("action")
                            if not isinstance(action, str):
                                continue

                            logger.info(f"{action.capitalize()} action recieved.")

                            match action:
                                case "start":
                                    try:
                                        server.start()
                                        await self._request_completed(
                                            websocket, request_id
                                        )
                                    except ServerIsAlreadyRunningError as e:
                                        await self._request_failed(
                                            websocket, request_id, str(e)
                                        )
                                case "stop":
                                    try:
                                        server.stop()
                                        await self._request_completed(
                                            websocket, request_id
                                        )
                                    except ServerIsNotRunningError as e:
                                        await self._request_failed(
                                            websocket, request_id, str(e)
                                        )
                                case "restart":
                                    try:
                                        server.restart()
                                        await self._request_completed(
                                            websocket, request_id
                                        )
                                    except (
                                        ServerIsNotRunningError,
                                        ServerStopTimeoutError,
                                        ServerIsAlreadyRunningError,
                                    ) as e:
                                        await self._request_failed(
                                            websocket, request_id, str(e)
                                        )
                        case "command":
                            command = message.get("command")
                            if not isinstance(command, str):
                                continue

                            logger.info("Command recieved.")

                            try:
                                server.execute_command(command)
                                await self._request_completed(websocket, request_id)
                            except ServerIsNotRunningError as e:
                                await self._request_failed(
                                    websocket, request_id, str(e)
                                )
                        case "files.get_item":
                            path = message.get("path")
                            if not isinstance(path, str) and path is not None:
                                continue

                            item = self.file_service.get_item(server, path)
                            if isinstance(item, FolderItem):
                                data = {
                                    "type": "folder",
                                    "name": item.name,
                                    "items": [
                                        {
                                            "type": "folder"
                                            if isinstance(item, FolderItem)
                                            else "file",
                                            "name": item.name,
                                        }
                                        for item in item.items
                                    ],
                                }
                                await self._request_completed(
                                    websocket, request_id, data
                                )
                            elif isinstance(item, FileItem):
                                data = {
                                    "type": "file",
                                    "name": item.name,
                                    "content": item.content,  # type: ignore
                                }
                                await self._request_completed(
                                    websocket, request_id, data
                                )
                            else:
                                await self._request_failed(
                                    websocket,
                                    request_id,
                                    "Item not found or access denied",
                                )
                        case "files.create_file":
                            path = message.get("path")
                            if not isinstance(path, str):
                                continue

                            content = message.get("content")
                            if content is not None and not isinstance(content, str):
                                continue

                            file = self.file_service.write_file(server, path, content)
                            if isinstance(file, FileItem):
                                await self._request_completed(websocket, request_id)
                            else:
                                await self._request_failed(
                                    websocket,
                                    request_id,
                                    "File exists or access denied",
                                )
                        case "files.create_folder":
                            path = message.get("path")
                            if not isinstance(path, str):
                                continue

                            folder = self.file_service.create_folder(server, path)
                            if isinstance(folder, FolderItem):
                                await self._request_completed(websocket, request_id)
                            else:
                                await self._request_failed(
                                    websocket,
                                    request_id,
                                    "Folder exists or access denied",
                                )
                        case "files.update_file":
                            path = message.get("path")
                            if not isinstance(path, str):
                                continue

                            new_path = message.get("new_path")
                            if new_path is not None and not isinstance(new_path, str):
                                continue

                            new_content = message.get("new_content")
                            if new_content is not None and not isinstance(
                                new_content, str
                            ):
                                continue

                            file = self.file_service.update_file(
                                server, path, new_path, new_content
                            )
                            if isinstance(file, FileItem):
                                await self._request_completed(websocket, request_id)
                            else:
                                await self._request_failed(
                                    websocket,
                                    request_id,
                                    "File not found or access denied",
                                )
                        case "files.update_folder":
                            path = message.get("path")
                            if not isinstance(path, str):
                                continue

                            new_path = message.get("new_path")
                            if new_path is None or not isinstance(new_path, str):
                                continue

                            folder = self.file_service.update_folder(
                                server, path, new_path
                            )
                            if isinstance(folder, FolderItem):
                                await self._request_completed(websocket, request_id)
                            else:
                                await self._request_failed(
                                    websocket,
                                    request_id,
                                    "Folder not found or access denied",
                                )
                        case "files.delete":
                            path = message.get("path")
                            if not isinstance(path, str):
                                continue

                            deleted = self.file_service.delete_item(server, path)
                            if deleted:
                                await self._request_completed(websocket, request_id)
                            else:
                                await self._request_failed(
                                    websocket,
                                    request_id,
                                    "File not found or access denied",
                                )
                        case "properties.get":
                            properties = self.properties_service.get_properties(server)
                            if properties:
                                await self._request_completed(
                                    websocket, request_id, properties
                                )
                            else:
                                await self._request_failed(
                                    websocket, request_id, "File not found"
                                )
                        case "properties.set":
                            property = message.get("property")
                            if not isinstance(property, str):
                                continue

                            new_value = message.get("new_value")
                            if not isinstance(new_value, str):
                                continue

                            setted = self.properties_service.set_property(
                                server, property, new_value
                            )
                            if setted:
                                await self._request_completed(websocket, request_id)
                            else:
                                await self._request_failed(
                                    websocket, request_id, "File or property not found"
                                )
                case "registered":
                    logger.info("All servers are registered.")
                case "registration_failed":
                    invalid_servers = message.get("servers")
                    if not isinstance(invalid_servers, list):
                        continue

                    if len(invalid_servers) == len(self._servers_by_key):
                        logger.critical(
                            "Registration failed. All daemon keys are invalid."
                        )
                        raise NoValidDaemonKeysError("All daemon keys are invalid.")
                    else:
                        logger.warning(
                            f"Registration failed. Invalid daemon keys: {', '.join([f'"{server.get("key")}"' for server in invalid_servers])}."
                        )
                        for invalid_server in invalid_servers:
                            if not isinstance(invalid_server, dict):
                                continue
                            key = invalid_server.get("key")
                            if isinstance(key, str):
                                self._servers_by_key.pop(key, None)
                case _:
                    continue

    async def _send_updates(self, websocket: ClientConnection) -> None:
        while True:
            servers = []

            for server in self._servers_by_key.values():
                servers.append(
                    {
                        "key": server.key,
                        "status": server.get_server_info(),
                        "metrics": self.metrics_service.get_metrics(server),
                        "logs": server.get_pending_logs(),
                    }
                )

            await self._send_json(websocket, {"type": "status", "servers": servers})
            await asyncio.sleep(1)

    async def connect(self) -> None:
        for _ in range(5):
            try:
                async with connect(self._api_uri) as websocket:
                    logger.info("Connection to API opened.")
                    register_message = {
                        "type": "register",
                        "servers": [
                            {"key": server_key}
                            for server_key in self._servers_by_key.keys()
                        ],
                    }
                    await self._send_json(websocket, register_message)
                    await asyncio.gather(
                        self._send_updates(websocket), self._recieve_commands(websocket)
                    )
                    while True:
                        await asyncio.sleep(1)
            except ConnectionClosed:
                logger.info("Connection to API closed.")
            except InvalidMessage:
                logger.error("Received invalid message from API")
            except NoValidDaemonKeysError:
                break
