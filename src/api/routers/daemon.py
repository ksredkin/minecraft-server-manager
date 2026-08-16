from fastapi import Depends, WebSocket
from fastapi.routing import APIRouter
from src.api.services.connection_manager import (
    ConnectionManager,
    get_connection_manager,
)

daemon_router = APIRouter()


@daemon_router.websocket("/ws/daemon")
async def daemon_websocket(
    websocket: WebSocket,
    connection_manager: ConnectionManager = Depends(get_connection_manager),
) -> None:
    await connection_manager.connect_and_recieve(websocket)
