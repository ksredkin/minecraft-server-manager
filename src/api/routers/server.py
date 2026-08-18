import asyncio
from datetime import datetime
from typing import Any, cast
from uuid import UUID

from fastapi import Depends, WebSocket, WebSocketDisconnect, WebSocketException
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from src.api.dependencies.auth import get_current_user_id, get_current_user_id_ws
from src.api.dependencies.server import get_server_service
from src.api.schemas.server import ServerDeletedResponse, ServerInfoResponse
from src.api.services.connection_manager import (
    ConnectionManager,
    get_connection_manager,
)
from src.api.services.server_service import ServerService
from src.common.database.models import Server

server_router = APIRouter(prefix="/servers")


@server_router.get(
    "/",
    response_model=list[ServerInfoResponse],
    status_code=200,
    description="Получить список серверов пользователя.",
)
async def get_servers(
    current_user_id: int = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service),
) -> list[ServerInfoResponse]:
    user_servers = await server_service.get_by_user(current_user_id)
    return [
        ServerInfoResponse.model_validate(cast(dict[str, Any], server))
        for server in user_servers
    ]


@server_router.post("/", status_code=201, description="Создать сервер.")
async def create_server(
    display_name: str | None = None,
    current_user_id: int = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service),
) -> dict[str, str | UUID | datetime]:
    server_created = await server_service.create_server(current_user_id, display_name)
    return {
        "uuid": server_created.uuid,
        "display_name": display_name or str(server_created.uuid),
        "daemon_key": server_created.daemon_key,
        "created_at": server_created.created_at,
    }


@server_router.delete(
    "/{uuid}",
    response_model=ServerDeletedResponse,
    status_code=200,
    description="Удалить сервер.",
)
async def delete_server(
    uuid: UUID,
    current_user_id: int = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service),
) -> JSONResponse | Server:
    deleted = await server_service.delete_for_user(current_user_id, uuid)

    if not deleted:
        return JSONResponse(
            content={
                "success": False,
                "error": "Server not found or you don't have permission to delete it",
            },
            status_code=404,
        )

    return deleted


@server_router.websocket("/{uuid}/ws")
async def server_websocket(
    uuid: UUID,
    websocket: WebSocket,
    current_user_id: int = Depends(get_current_user_id_ws),
    connection_manager: ConnectionManager = Depends(get_connection_manager),
    server_service: ServerService = Depends(get_server_service),
) -> None:
    try:
        server_id = await server_service.get_server_id(uuid)
        if not server_id or not await server_service.is_viewer_or_above(
            current_user_id, server_id
        ):
            raise WebSocketException(code=1008)

        await connection_manager.connect_and_subscribe_to_server_channel(
            websocket, server_id
        )
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass


@server_router.post("/{uuid}/start", status_code=200, description="Запустить сервер.")
async def start_server(
    uuid: UUID,
    current_user_id: int = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service),
    connection_manager: ConnectionManager = Depends(get_connection_manager),
) -> JSONResponse:
    server_id = await server_service.get_server_id(uuid)
    if not server_id:
        return JSONResponse(
            content={
                "success": False,
                "error": "Server not found or you don't have permission to start it",
            },
            status_code=404,
        )

    if not await server_service.is_admin_or_above(current_user_id, server_id):
        return JSONResponse(
            content={
                "success": False,
                "error": "Server not found or you don't have permission to start it",
            },
            status_code=404,
        )

    result = await connection_manager.send_action_to_server(server_id, "start")
    if not result:
        return JSONResponse(
            content={
                "success": False,
                "error": "Daemon is disconnected or an internal error occurred",
            },
            status_code=503,
        )

    if result.get("type") == "action_completed":
        return JSONResponse(content={"success": True})
    return JSONResponse(
        content={"success": False, "error": result.get("error")}, status_code=409
    )


@server_router.post("/{uuid}/stop", status_code=200, description="Остановить сервер.")
async def stop_server(
    uuid: UUID,
    current_user_id: int = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service),
    connection_manager: ConnectionManager = Depends(get_connection_manager),
) -> JSONResponse:
    server_id = await server_service.get_server_id(uuid)
    if not server_id:
        return JSONResponse(
            content={
                "success": False,
                "error": "Server not found or you don't have permission to stop it",
            },
            status_code=404,
        )

    if not await server_service.is_admin_or_above(current_user_id, server_id):
        return JSONResponse(
            content={
                "success": False,
                "error": "Server not found or you don't have permission to stop it",
            },
            status_code=404,
        )

    result = await connection_manager.send_action_to_server(server_id, "stop")
    if not result:
        return JSONResponse(
            content={
                "success": False,
                "error": "Daemon is disconnected or an internal error occurred",
            },
            status_code=503,
        )

    if result.get("type") == "action_completed":
        return JSONResponse(content={"success": True})
    return JSONResponse(
        content={"success": False, "error": result.get("error")}, status_code=409
    )
