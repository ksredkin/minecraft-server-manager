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

logger = Logger(__name__)


class APIClient:
    def __init__(self, api_host: str, api_port: int, servers: list[Server]):
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
                        break

                    key = message.get("key")
                    if not isinstance(key, str):
                        continue

                    server = self._servers_by_key.get(key)
                    if not isinstance(server, Server):
                        continue

                    logger.info(f"{action.capitalize()} action recieved.")

                    action_id = message.get("id")
                    if not isinstance(action_id, str):
                        break

                    match action:
                        case "start":
                            try:
                                server.start()
                                await self._send_json(
                                    websocket,
                                    {"id": action_id, "type": "action_completed"},
                                )
                            except ServerIsAlreadyRunningError as e:
                                await self._send_json(
                                    websocket,
                                    {
                                        "id": action_id,
                                        "type": "action_failed",
                                        "error": str(e),
                                    },
                                )
                        case "stop":
                            try:
                                server.stop()
                                await self._send_json(
                                    websocket,
                                    {"id": action_id, "type": "action_completed"},
                                )
                            except ServerIsNotRunningError as e:
                                await self._send_json(
                                    websocket,
                                    {
                                        "id": action_id,
                                        "type": "action_failed",
                                        "error": str(e),
                                    },
                                )
                        case "restart":
                            try:
                                server.restart()
                                await self._send_json(
                                    websocket,
                                    {"id": action_id, "type": "action_completed"},
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
                                        "type": "action_failed",
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
