from fastapi import Depends, WebSocket
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse

from src.api.services.connection_manager import get_connection_manager, ConnectionManager
import json
from src.api.dependencies.daemon_key import get_daemon_key_service
from src.api.dependencies.server import get_server_service
from src.api.dependencies.server_user import get_server_user_service
from src.api.services.daemon_key_service import DaemonKeyService
from src.api.services.server_service import ServerService
from src.api.services.server_user_service import ServerUserService
from src.api.dependencies.auth import get_current_user_id
from src.api.dependencies.database import get_async_sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker
from src.api.services.key_service import KeyService
from src.api.dependencies.daemon_key import get_key_service
from src.common.repositories.daemon_key_repository import DaemonKeyRepository


daemon_router = APIRouter()

@daemon_router.websocket("/ws/daemon")
async def daemon_websocket(websocket: WebSocket, connection_manager: ConnectionManager = Depends(get_connection_manager), key_service: KeyService = Depends(get_key_service), sessionmaker: async_sessionmaker = Depends(get_async_sessionmaker)):
    connection_id = None
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
                            repository = DaemonKeyRepository(session)
                            daemon_key_service = DaemonKeyService(repository, key_service)
                            for server in servers:
                                if not isinstance(server, dict):
                                    continue

                                key = server.get("key")
                                if not isinstance(key, str):
                                    continue

                                server_id = await daemon_key_service.resolve_server_id(key)
                                if not server_id:
                                    continue

                                connection_manager.register_server_route(server_id, connection_id, key)
                                registered.append(key)
                                print(connection_manager.connections, flush=True)
                                print(connection_manager.server_routes, flush=True)
                        if len(registered) == len(servers):
                            await websocket.send_text(json.dumps({"type": "registered", "servers": servers}))
                        elif len(registered) > 0:
                            await websocket.send_text(json.dumps({"type": "registration_failed", "servers": [{**server, "error": "invalid_key"} for server in servers]}))
                        else:
                            await websocket.send_text(json.dumps({"type": "registration_failed", "servers": [{**server, "error": "invalid_key"} for server in servers]}))
    except Exception as e:
        if connection_id:
            await connection_manager.disconnect(connection_id)

@daemon_router.post("/daemon/key")
async def create_daemon_key(server_uuid: str, current_user_id: int = Depends(get_current_user_id), daemon_key_service: DaemonKeyService = Depends(get_daemon_key_service), server_service: ServerService = Depends(get_server_service), server_user_service: ServerUserService = Depends(get_server_user_service)) -> JSONResponse:
    server = await server_service.get_by_uuid(server_uuid)

    if not server:
        return JSONResponse(content={"success": False, "error": "Server not found or you don't have permission to create daemon keys for it"}, status_code=404)

    server_user = await server_user_service.get_by_user_and_server(current_user_id, server.id)

    if not server_user or not server_user_service.is_owner(server_user):
        return JSONResponse(content={"success": False, "error": "Server not found or you don't have permission to create daemon keys for it"}, status_code=404)

    key = await daemon_key_service.create_daemon_key(server.id)
    return JSONResponse(content={"succes": True, "key": key}, status_code=201)
