import asyncio
import json
from typing import Any

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
from src.daemon.services.metrics_service import MetricsService
from src.daemon.services.file_service import FileService, FileItem, FolderItem

logger = Logger(__name__)


class APIClient:
    def __init__(
        self,
        api_host: str,
        api_port: int,
        servers: list[Server],
        metrics_service: MetricsService,
        file_service: FileService,
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

    async def _send_json(self, websocket: ClientConnection, data: Any) -> None:
        await websocket.send(json.dumps(data), text=True)

    async def _recieve_commands(self, websocket: ClientConnection) -> None:
        while True:
            message: dict[str, str | list[dict[str, str]]] = json.loads(
                await websocket.recv()
            )
            if not isinstance(message, dict):
                continue

            message_type = message.get("type")
            match message_type:
                case "action":
                    action = message.get("action")
                    if not isinstance(action, str):
                        continue

                    key = message.get("key")
                    if not isinstance(key, str):
                        continue

                    server = self._servers_by_key.get(key)
                    if not isinstance(server, Server):
                        continue

                    logger.info(f"{action.capitalize()} action recieved.")

                    action_id = message.get("id")
                    if not isinstance(action_id, str):
                        continue

                    match action:
                        case "start":
                            try:
                                server.start()
                                await self._send_json(
                                    websocket,
                                    {"id": action_id, "type": "request_completed"},
                                )
                            except ServerIsAlreadyRunningError as e:
                                await self._send_json(
                                    websocket,
                                    {
                                        "id": action_id,
                                        "type": "request_failed",
                                        "error": str(e),
                                    },
                                )
                        case "stop":
                            try:
                                server.stop()
                                await self._send_json(
                                    websocket,
                                    {"id": action_id, "type": "request_completed"},
                                )
                            except ServerIsNotRunningError as e:
                                await self._send_json(
                                    websocket,
                                    {
                                        "id": action_id,
                                        "type": "request_failed",
                                        "error": str(e),
                                    },
                                )
                        case "restart":
                            try:
                                server.restart()
                                await self._send_json(
                                    websocket,
                                    {"id": action_id, "type": "request_completed"},
                                )
                            except (
                                ServerIsNotRunningError,
                                ServerStopTimeoutError,
                                ServerIsAlreadyRunningError,
                            ) as e:
                                await self._send_json(
                                    websocket,
                                    {
                                        "id": action_id,
                                        "type": "request_failed",
                                        "error": str(e),
                                    },
                                )
                case "command":
                    command = message.get("command")
                    if not isinstance(command, str):
                        continue

                    key = message.get("key")
                    if not isinstance(key, str):
                        continue

                    server = self._servers_by_key.get(key)
                    if not isinstance(server, Server):
                        continue

                    logger.info(f"Command recieved.")

                    command_id = message.get("id")
                    if not isinstance(command_id, str):
                        continue

                    try:
                        server.execute_command(command)
                        await self._send_json(
                            websocket,
                            {"id": command_id, "type": "request_completed"},
                        )
                    except ServerIsNotRunningError as e:
                        await self._send_json(
                            websocket,
                            {
                                "id": command_id,
                                "type": "request_failed",
                                "error": str(e),
                            },
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
                case "files.get_item":
                    path = message.get("path")
                    if not isinstance(path, str) and path is not None:
                        continue

                    key = message.get("key")
                    if not isinstance(key, str):
                        continue

                    server = self._servers_by_key.get(key)
                    if not isinstance(server, Server):
                        continue

                    request_id = message.get("id")
                    if not isinstance(request_id, str):
                        continue

                    item = self.file_service.get_item(server, path)
                    if isinstance(item, FolderItem):
                        await self._send_json(
                            websocket,
                            {
                                "id": request_id,
                                "type": "request_completed",
                                "item": {
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
                                },
                            },
                        )
                    elif isinstance(item, FileItem):
                        await self._send_json(
                            websocket,
                            {
                                "id": request_id,
                                "type": "request_completed",
                                "item": {
                                    "type": "file",
                                    "name": item.name,
                                    "content": item.content,
                                },
                            },
                        )
                    else:
                        await self._send_json(
                            websocket,
                            {
                                "id": request_id,
                                "type": "request_failed",
                                "error": "Item not found or access denied",
                            },
                        )
                case "files.create_file":
                    path = message.get("path")
                    if not isinstance(path, str):
                        continue

                    content = message.get("content")
                    if content is not None and not isinstance(content, str):
                        continue

                    key = message.get("key")
                    if not isinstance(key, str):
                        continue

                    server = self._servers_by_key.get(key)
                    if not isinstance(server, Server):
                        continue

                    request_id = message.get("id")
                    if not isinstance(request_id, str):
                        continue

                    file = self.file_service.write_file(server, path, content)
                    if isinstance(file, FileItem):
                        await self._send_json(
                            websocket,
                            {
                                "id": request_id,
                                "type": "request_completed",
                            },
                        )
                    else:
                        await self._send_json(
                            websocket,
                            {
                                "id": request_id,
                                "type": "request_failed",
                                "error": "File exists or access denied",
                            },
                        )
                case "files.create_folder":
                    path = message.get("path")
                    if not isinstance(path, str):
                        continue

                    key = message.get("key")
                    if not isinstance(key, str):
                        continue

                    server = self._servers_by_key.get(key)
                    if not isinstance(server, Server):
                        continue

                    request_id = message.get("id")
                    if not isinstance(request_id, str):
                        continue

                    folder = self.file_service.create_folder(server, path)
                    if isinstance(folder, FolderItem):
                        await self._send_json(
                            websocket,
                            {
                                "id": request_id,
                                "type": "request_completed",
                            },
                        )
                    else:
                        await self._send_json(
                            websocket,
                            {
                                "id": request_id,
                                "type": "request_failed",
                                "error": "Folder exists or access denied",
                            },
                        )
                case "files.update_file":
                    path = message.get("path")
                    if not isinstance(path, str):
                        continue

                    new_path = message.get("new_path")
                    if new_path is not None and not isinstance(new_path, str):
                        continue

                    new_content = message.get("new_content")
                    if new_content is not None and not isinstance(new_content, str):
                        continue

                    key = message.get("key")
                    if not isinstance(key, str):
                        continue

                    server = self._servers_by_key.get(key)
                    if not isinstance(server, Server):
                        continue

                    request_id = message.get("id")
                    if not isinstance(request_id, str):
                        continue

                    file = self.file_service.update_file(
                        server, path, new_path, new_content
                    )
                    if isinstance(file, FileItem):
                        await self._send_json(
                            websocket,
                            {
                                "id": request_id,
                                "type": "request_completed",
                            },
                        )
                    else:
                        await self._send_json(
                            websocket,
                            {
                                "id": request_id,
                                "type": "request_failed",
                                "error": "File not found or access denied",
                            },
                        )

                case "files.update_folder":
                    path = message.get("path")
                    if not isinstance(path, str):
                        continue

                    new_path = message.get("new_path")
                    if new_path is not None and not isinstance(new_path, str):
                        continue

                    key = message.get("key")
                    if not isinstance(key, str):
                        continue

                    server = self._servers_by_key.get(key)
                    if not isinstance(server, Server):
                        continue

                    request_id = message.get("id")
                    if not isinstance(request_id, str):
                        continue

                    folder = self.file_service.update_folder(server, path, new_path)
                    if isinstance(folder, FolderItem):
                        await self._send_json(
                            websocket,
                            {
                                "id": request_id,
                                "type": "request_completed",
                            },
                        )
                    else:
                        await self._send_json(
                            websocket,
                            {
                                "id": request_id,
                                "type": "request_failed",
                                "error": "Folder not found or access denied",
                            },
                        )
                case "files.delete":
                    path = message.get("path")
                    if not isinstance(path, str):
                        continue

                    key = message.get("key")
                    if not isinstance(key, str):
                        continue

                    server = self._servers_by_key.get(key)
                    if not isinstance(server, Server):
                        continue

                    request_id = message.get("id")
                    if not isinstance(request_id, str):
                        continue

                    deleted = self.file_service.delete_item(server, path)
                    if deleted:
                        await self._send_json(
                            websocket,
                            {
                                "id": request_id,
                                "type": "request_completed",
                            },
                        )
                    else:
                        await self._send_json(
                            websocket,
                            {
                                "id": request_id,
                                "type": "request_failed",
                                "error": "File not found or access denied",
                            },
                        )
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
