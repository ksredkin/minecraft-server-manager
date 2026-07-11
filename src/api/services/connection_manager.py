from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: list[WebSocket] = []

    async def connect(self, connection: WebSocket) -> None:
        await connection.accept()
        self.connections.append(connection)

    async def broadcast(self, message: str) -> None:
        dead_connections = []
        for connection in self.connections:
            try:
                await connection.send_text(message)
            except Exception:
                dead_connections.append(connection)
        self.connections = [c for c in self.connections if c not in dead_connections]

    async def disconnect(self, connection: WebSocket) -> None:
        self.connections.remove(connection)


connection_manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    return connection_manager
