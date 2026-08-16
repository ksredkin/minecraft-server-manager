import asyncio
import json
from typing import Any

from websockets import ClientConnection, connect
from websockets.exceptions import ConnectionClosed

from src.common.utils.logger import Logger
from src.daemon.exceptions.server import ServerIsAlreadyRunningError
from src.daemon.server import Server

logger = Logger(__name__)


class APIClient:
    def __init__(self, api_host: str, api_port: int, servers: list[Server]):
        if not api_host:
            raise ValueError(
                "В конфигурации daemon не установлено значение для api_host."
            )

        if not api_port:
            raise ValueError(
                "В конфигурации daemon не установлено значение для api_port."
            )

        self._api_uri = f"ws://{api_host}:{api_port}/ws/daemon"
        self._servers_by_key = {server.key: server for server in servers}

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
                case "registered":
                    logger.info("All servers are registered.")
                case "registration_failed":
                    invalid_servers: list[dict[str, str]] | str | None = message.get(
                        "servers"
                    )
                    if not isinstance(invalid_servers, list):
                        continue

                    if len(invalid_servers) == len(self._servers_by_key):
                        logger.critical(
                            "Registration failed. All daemon keys are invalid."
                        )
                    else:
                        logger.warning(
                            f"Registration failed. Invalid daemon keys: {', '.join([f'"{server.get("key")}"' for server in invalid_servers])}."
                        )
                case _:
                    continue

    async def _send_status(self, websocket: ClientConnection) -> None:
        while True:
            message = {"type": "status"}
            await self._send_json(websocket, message)
            await asyncio.sleep(1)

    async def connect(self) -> None:
        for _ in range(5):
            async with connect(self._api_uri) as websocket:
                try:
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
                        self._send_status(websocket), self._recieve_commands(websocket)
                    )
                    while True:
                        await asyncio.sleep(1)
                except ConnectionClosed:
                    logger.info("Connection to API closed.")
