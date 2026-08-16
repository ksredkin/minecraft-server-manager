import asyncio
import json

from websockets import ClientConnection, connect

from src.daemon.server import Server
from src.daemon.exceptions.server import ServerIsAlreadyRunningError


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

    async def _recieve_commands(self, websocket: ClientConnection) -> None:
        while True:
            message: dict[str, str] = json.loads(await websocket.recv())
            if not isinstance(message, dict):
                continue

            key = message.get("key")
            if not isinstance(key, str):
                continue

            server = self._servers_by_key.get(key)
            if not isinstance(server, Server):
                continue

            message_type = message.get("type")
            match message_type:
                case "action":
                    action = message.get("action")
                    if not isinstance(action, str):
                        break

                    action_id = message.get("id")
                    if not isinstance(action_id, str):
                        break

                    match action:
                        case "start":
                            try:
                                server.start()
                                await websocket.send(
                                    json.dumps(
                                        {"id": action_id, "type": "action_completed"}
                                    )
                                )
                            except ServerIsAlreadyRunningError as e:
                                await websocket.send(
                                    json.dumps(
                                        {
                                            "id": action_id,
                                            "type": "action_failed",
                                            "error": str(e),
                                        }
                                    )
                                )
                case _:
                    continue

    async def _send_status(self, websocket: ClientConnection) -> None:
        while True:
            message = {"type": "status"}
            await websocket.send(json.dumps(message), text=True)
            await asyncio.sleep(1)

    async def connect(self) -> None:
        for _ in range(5):
            async with connect(self._api_uri) as websocket:
                try:
                    register_message = {
                        "type": "register",
                        "servers": [
                            {"key": server_key}
                            for server_key in self._servers_by_key.keys()
                        ],
                    }
                    await websocket.send(json.dumps(register_message), text=True)
                    await asyncio.gather(
                        self._send_status(websocket), self._recieve_commands(websocket)
                    )
                    while True:
                        await asyncio.sleep(1)
                except Exception as e:
                    raise e
