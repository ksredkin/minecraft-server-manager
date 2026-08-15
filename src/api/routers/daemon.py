import json

from fastapi import Depends, WebSocket
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.api.dependencies.database import get_async_sessionmaker
from src.api.dependencies.server import get_key_service
from src.api.services.connection_manager import (
    ConnectionManager,
    get_connection_manager,
)
from src.api.services.key_service import KeyService
from src.api.services.server_service import ServerService
from src.api.services.server_user_service import ServerUserService
from src.common.repositories.server_repository import ServerRepository
from src.common.repositories.server_user_repository import ServerUserRepository
from src.common.services.cache_service import CacheService, get_cache_service

daemon_router = APIRouter()


@daemon_router.websocket("/ws/daemon")
async def daemon_websocket(
    websocket: WebSocket,
    connection_manager: ConnectionManager = Depends(get_connection_manager),
    key_service: KeyService = Depends(get_key_service),
    sessionmaker: async_sessionmaker[AsyncSession] = Depends(get_async_sessionmaker),
    cache_service: CacheService = Depends(get_cache_service),
) -> None:
    connection_id: int | None = None
    try:
        connection_id = await connection_manager.connect(websocket)
        need_to_disconnect = False
        while True:
            if need_to_disconnect:
                await websocket.close()
                break

            message = json.loads(await websocket.receive_text())
            if not isinstance(message, dict):
                return

            match message.get("type"):
                case "register":
                    servers = message.get("servers")
                    if isinstance(servers, list):
                        registered = []
                        async with sessionmaker() as session:
                            daemon_key_service = ServerService(
                                ServerRepository(session),
                                key_service,
                                ServerUserService(
                                    ServerUserRepository(session), cache_service
                                ),
                                cache_service,
                            )
                            for server in servers:
                                if not isinstance(server, dict):
                                    continue

                                key = server.get("key")
                                if not isinstance(key, str):
                                    continue

                                server_id = await daemon_key_service.resolve_server_id(
                                    key
                                )
                                if not server_id:
                                    continue

                                connection_manager.register_server_route(
                                    server_id, connection_id, key
                                )
                                registered.append(key)
                        if len(registered) == len(servers):
                            await websocket.send_text(
                                json.dumps({"type": "registered", "servers": servers})
                            )
                        elif len(registered) > 0:
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "registration_failed",
                                        "servers": [
                                            {**server, "error": "invalid_key"}
                                            for server in servers
                                        ],
                                    }
                                )
                            )
                        else:
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "registration_failed",
                                        "servers": [
                                            {**server, "error": "invalid_key"}
                                            for server in servers
                                        ],
                                    }
                                )
                            )
    except Exception as e:
        if connection_id:
            await connection_manager.disconnect(connection_id)
        raise e
