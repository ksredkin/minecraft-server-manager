from websockets import connect, ClientConnection
from src.daemon.server import Server
import asyncio
import json

class APIClient:
    def __init__(self, api_host: str, api_port: int, servers: list[Server]):
        if not api_host:
            raise ValueError("В конфигурации daemon не установлено значение для api_host.")

        if not api_port:
            raise ValueError("В конфигурации daemon не установлено значение для api_port.")

        self._api_uri = f"ws://{api_host}:{api_port}/ws/daemon"
        self._servers = servers

    async def _recieve_commands(self, websocket: ClientConnection):
        while True:
            message = json.loads(await websocket.recv())
            print(message)

    async def _send_status(self, websocket: ClientConnection):
        while True:
            message = {"type": "status"}
            await websocket.send(json.dumps(message), text=True)
            await asyncio.sleep(1)

    async def connect(self):
        for _ in range(5):
            async with connect(self._api_uri) as websocket:
                try:
                    register_message = {"type": "register", "servers": [{"key": server.key} for server in self._servers]}
                    await websocket.send(json.dumps(register_message), text=True)
                    await asyncio.gather(self._send_status(websocket), self._recieve_commands(websocket))
                    while True:
                        await asyncio.sleep(1)
                except Exception as e:
                    raise e

