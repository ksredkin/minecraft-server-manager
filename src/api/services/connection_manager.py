from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.connections: dict[int, WebSocket] = {}
        self.server_routes: dict[int, dict[str, str]] = {}

    async def connect(self, connection: WebSocket) -> int:
        await connection.accept()
        connection_id = max(self.connections.keys(), default=0) + 1
        self.connections[connection_id] = connection
        print(self.connections, flush=True)
        return connection_id

    def register_server_route(self, server_id: int, connection_id: int, key: str):
        self.server_routes[server_id] = {"connection_id": connection_id, "key": key}

    async def disconnect(self, connection_id: int):
        if connection_id in self.connections.keys():
            self.connections.pop(connection_id)

connection_manager = ConnectionManager()

def get_connection_manager() -> ConnectionManager:
    return connection_manager