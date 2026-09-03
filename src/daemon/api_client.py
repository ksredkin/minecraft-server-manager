import asyncio
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID

import aiofiles
from websockets import ClientConnection, connect
from websockets.exceptions import ConnectionClosed, InvalidMessage

from src.common.utils.logger import Logger
from src.daemon.exceptions.api_client import NoValidDaemonKeysError
from src.daemon.exceptions.backup import (
    BackupAlreadyExistsError,
    BackupNotFoundError,
    BackupStorageFullError,
)
from src.daemon.exceptions.config import InvalidConfigError
from src.daemon.exceptions.server import (
    ServerIsAlreadyRunningError,
    ServerIsNotRunningError,
    ServerStopTimeoutError,
)
from src.daemon.server import Server
from src.daemon.services.backup_service import Backup, BackupService
from src.daemon.services.eula_service import EulaService
from src.daemon.services.file_service import FileItem, FileService, FolderItem
from src.daemon.services.metrics_service import MetricsService
from src.daemon.services.properties_service import PropertiesService
from src.daemon.services.storage_service import StorageService

logger = Logger(__name__)


class TransferKind(Enum):
    BACKUP = "backup"
    PLUGIN = "plugin"


@dataclass
class Transfer:
    path: Path
    kind: TransferKind


class APIClient:
    def __init__(
        self,
        api_host: str,
        api_port: int,
        servers: list[Server],
        metrics_service: MetricsService,
        file_service: FileService,
        properties_service: PropertiesService,
        eula_service: EulaService,
        backup_service: BackupService,
        storage_service: StorageService,
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
        self.eula_service = eula_service
        self.backup_service = backup_service
        self.storage_service = storage_service

        self._accepted_transfers: dict[UUID, Transfer] = {}

    async def _send_json(self, websocket: ClientConnection, data: Any) -> None:
        await websocket.send(json.dumps(data), text=True)

    async def _send_bytes(self, websocket: ClientConnection, data: bytes) -> None:
        await websocket.send(data)

    async def _request_failed(
        self, websocket: ClientConnection, request_id: UUID, error: str | None = None
    ) -> None:
        message = {"id": str(request_id), "type": "request_failed"}
        if error is not None:
            message["error"] = error
        await self._send_json(websocket, message)

    async def _request_completed(
        self, websocket: ClientConnection, request_id: UUID, data: Any | None = None
    ) -> None:
        message = {"id": str(request_id), "type": "request_completed"}
        if data is not None:
            message["data"] = data
        await self._send_json(websocket, message)

    async def _request_accepted(
        self, websocket: ClientConnection, request_id: UUID, data: Any | None = None
    ) -> None:
        message = {"id": str(request_id), "type": "request_accepted"}
        if data is not None:
            message["data"] = data
        await self._send_json(websocket, message)

    async def _request_rejected(
        self, websocket: ClientConnection, request_id: UUID, data: Any | None = None
    ) -> None:
        message = {"id": str(request_id), "type": "request_rejected"}
        if data is not None:
            message["data"] = data
        await self._send_json(websocket, message)

    async def _create_backup(
        self, websocket: ClientConnection, request_id: UUID, server: Server
    ) -> None:
        try:
            backup = await asyncio.to_thread(self.backup_service.create, server)
            await self._request_completed(
                websocket, request_id, {"name": backup.name, "size": backup.size}
            )
        except Exception as e:
            await self._request_failed(websocket, request_id, str(e))

    async def _restore_backup(
        self, websocket: ClientConnection, request_id: UUID, server: Server, backup: str
    ) -> None:
        try:
            await asyncio.to_thread(self.backup_service.restore_backup, server, backup)
            await self._request_completed(websocket, request_id)
        except Exception as e:
            await self._request_failed(websocket, request_id, str(e))

    async def _upload_backup(
        self, websocket: ClientConnection, request_id: UUID, backup: Backup
    ) -> None:
        try:
            async with aiofiles.open(backup.path, "rb") as f:
                while True:
                    chunk = await f.read(1024 * 1024)
                    if not chunk:
                        break

                    await self._send_bytes(websocket, request_id.bytes + chunk)

            await self._request_completed(websocket, request_id)
        except Exception as e:
            await self._request_failed(websocket, request_id, str(e))

    def _accept_transfer(
        self, request_id: UUID, path: Path, transfer_kind: TransferKind
    ) -> None:
        self._accepted_transfers[request_id] = Transfer(path, transfer_kind)

    def _accept_backup(self, request_id: UUID, path: Path) -> None:
        self._accept_transfer(request_id, path, TransferKind.BACKUP)

    async def _recieve_commands(self, websocket: ClientConnection) -> None:
        while True:
            recieved = await websocket.recv()

            if isinstance(recieved, bytes):
                request_id_bytes = recieved[:16]
                chunk = recieved[16:]
                if not isinstance(request_id_bytes, bytes) or not isinstance(
                    chunk, bytes
                ):
                    continue

                try:
                    request_id = UUID(bytes=request_id_bytes)
                except ValueError:
                    continue

                if request_id not in self._accepted_transfers.keys():
                    continue

                transfer = self._accepted_transfers[request_id]

                if transfer.kind == TransferKind.BACKUP:
                    self.backup_service.handle_chunk(transfer.path, chunk)
                    self.storage_service.add_progress(request_id, len(chunk))

            if isinstance(recieved, str):
                message: dict[str, str | list[dict[str, str]]] = json.loads(recieved)
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
                        | "eula.get"
                        | "eula.set"
                        | "backups.create"
                        | "backups.delete"
                        | "backups.get"
                        | "backups.restore"
                        | "backups.upload"
                        | "backups.get_all"
                        | "backups.download"
                        | "backups.free_storage"
                        | "backups.download"
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

                                file = self.file_service.write_file(
                                    server, path, content
                                )
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
                                if new_path is not None and not isinstance(
                                    new_path, str
                                ):
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
                                properties = self.properties_service.get_properties(
                                    server
                                )
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
                                        websocket,
                                        request_id,
                                        "File or property not found",
                                    )
                            case "eula.get":
                                eula = self.eula_service.get(server)
                                if eula is not None:
                                    await self._request_completed(
                                        websocket, request_id, eula
                                    )
                                else:
                                    await self._request_failed(
                                        websocket,
                                        request_id,
                                        "File or property not found",
                                    )
                            case "eula.set":
                                accept = message.get("accept")
                                if not isinstance(accept, bool):
                                    continue

                                setted = self.eula_service.set(server, accept)
                                if setted:
                                    await self._request_completed(websocket, request_id)
                                else:
                                    await self._request_failed(
                                        websocket,
                                        request_id,
                                        "File or property not found",
                                    )
                            case "backups.create":
                                asyncio.create_task(
                                    self._create_backup(websocket, request_id, server)
                                )
                                await self._request_accepted(websocket, request_id)
                            case "backups.delete":
                                backup = message.get("backup")
                                if not isinstance(backup, str):
                                    continue

                                try:
                                    self.backup_service.delete_backup(server, backup)
                                    await self._request_completed(websocket, request_id)
                                except Exception as e:
                                    await self._request_failed(
                                        websocket, request_id, str(e)
                                    )
                            case "backups.restore":
                                backup = message.get("backup")
                                if not isinstance(backup, str):
                                    continue

                                asyncio.create_task(
                                    self._restore_backup(
                                        websocket, request_id, server, backup
                                    )
                                )
                                await self._request_accepted(websocket, request_id)
                            case "backups.get_all":
                                try:
                                    backups = self.backup_service.get_backups(server)
                                    await self._request_completed(
                                        websocket,
                                        request_id,
                                        [
                                            {"name": backup.name, "size": backup.size}
                                            for backup in backups
                                        ],
                                    )
                                except Exception as e:
                                    await self._request_failed(
                                        websocket, request_id, str(e)
                                    )
                            case "backups.get":
                                backup = message.get("backup")
                                if not isinstance(backup, str):
                                    continue

                                getted_backup = self.backup_service.get_backup(
                                    server, backup
                                )
                                if getted_backup is not None:
                                    await self._request_completed(
                                        websocket,
                                        request_id,
                                        {
                                            "name": getted_backup.name,
                                            "size": getted_backup.size,
                                        },
                                    )
                                else:
                                    await self._request_failed(
                                        websocket, request_id, "Backup not found."
                                    )
                            case "backups.upload":
                                backup = message.get("backup")
                                if not isinstance(backup, str):
                                    continue

                                try:
                                    getted_backup = self.backup_service.get_backup(
                                        server, backup
                                    )
                                    if not getted_backup:
                                        raise BackupNotFoundError("Backup not found.")

                                    asyncio.create_task(
                                        self._upload_backup(
                                            websocket, request_id, getted_backup
                                        )
                                    )
                                    await self._request_accepted(
                                        websocket,
                                        request_id,
                                        {"total": getted_backup.size},
                                    )
                                except Exception as e:
                                    await self._request_rejected(
                                        websocket, request_id, {"error": str(e)}
                                    )
                            case "backups.free_storage":
                                free_storage = self.storage_service.get_disk_free_space(
                                    self.backup_service.backups_dir
                                )
                                await self._request_completed(
                                    websocket, request_id, {"free": free_storage}
                                )
                            case "backups.download":
                                try:
                                    size = message.get("size")
                                    if not isinstance(size, int):
                                        continue

                                    backup_name = message.get("backup")
                                    if not isinstance(backup_name, str):
                                        continue

                                    existing_backup = self.backup_service.get_backup(
                                        server, backup_name
                                    )
                                    if existing_backup:
                                        raise BackupAlreadyExistsError(
                                            "Backup already exists."
                                        )

                                    free_storage = (
                                        self.storage_service.get_disk_free_space(
                                            self.backup_service.backups_dir
                                        )
                                    )
                                    if free_storage < size:
                                        raise BackupStorageFullError(
                                            "Backup storage is full."
                                        )

                                    backup_path = (
                                        self.backup_service.backups_dir / backup_name
                                    ).with_suffix(".zip")
                                    self.storage_service.reserve(
                                        backup_path, request_id, size
                                    )
                                    self._accept_backup(request_id, backup_path)

                                    await self._request_accepted(websocket, request_id)
                                except Exception as e:
                                    await self._request_rejected(
                                        websocket, request_id, {"error": str(e)}
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
                async with connect(
                    self._api_uri, max_size=8 * 1024 * 1024
                ) as websocket:
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
            except Exception as e:
                logger.error(f"API connection failed: {e}", exc_info=True)
