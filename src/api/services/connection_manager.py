from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: list[WebSocket] = []

    async def connect(self, connection: WebSocket) -> None:
        await connection.accept()
        self.connections.append(connection)

    async def broadcast(self, message: str) -> None:
        for connection in self.connections:
            await connection.send_text(message)


connection_manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    return connection_manager
