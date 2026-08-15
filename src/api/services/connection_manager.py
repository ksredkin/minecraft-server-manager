from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: dict[int, WebSocket] = {}
        self.server_routes: dict[int, dict[str, str | int]] = {}

    async def connect(self, connection: WebSocket) -> int:
        await connection.accept()
        connection_id = max(self.connections.keys(), default=0) + 1
        self.connections[connection_id] = connection
        return connection_id

    def register_server_route(
        self, server_id: int, connection_id: int, key: str
    ) -> None:
        self.server_routes[server_id] = {"connection_id": connection_id, "key": key}

    async def disconnect(self, connection_id: int) -> None:
        if connection_id in self.connections.keys():
            self.connections.pop(connection_id)

    async def send_message_to_server(
        self, server_id: int, message_type: str, **payload: str
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
            await connection.send_json({"type": message_type, "key": key, **payload})
            return True
        except Exception:
            return False

    async def send_action_to_server(self, server_id: int, action: str) -> bool:
        return await self.send_message_to_server(server_id, "action", action=action)

    async def send_command_to_server(self, server_id: int, command: str) -> bool:
        return await self.send_message_to_server(server_id, "command", command=command)


connection_manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    return connection_manager
