import asyncio
from datetime import datetime
from typing import Any, cast
from uuid import UUID

from fastapi import Depends, WebSocket, WebSocketDisconnect, WebSocketException
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from src.api.dependencies.auth import get_current_user_id, get_current_user_id_ws
from src.api.dependencies.server import get_server_service
from src.api.exceptions.server import ServerNotFoundError
from src.api.schemas.server import (
    FileCreateRequest,
    FileUpdateRequest,
    ServerDeletedResponse,
    ServerInfoResponse,
)
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
    if not server_id or not await server_service.is_admin_or_above(
        current_user_id, server_id
    ):
        raise ServerNotFoundError("Server not found or access denied")

    result = await connection_manager.execute_server_action(server_id, "start")
    message: dict[str, str | bool] = {"success": result.success}
    if result.error:
        message["error"] = result.error

    return JSONResponse(content=message, status_code=result.status_code)


@server_router.post("/{uuid}/stop", status_code=200, description="Остановить сервер.")
async def stop_server(
    uuid: UUID,
    current_user_id: int = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service),
    connection_manager: ConnectionManager = Depends(get_connection_manager),
) -> JSONResponse:
    server_id = await server_service.get_server_id(uuid)
    if not server_id or not await server_service.is_admin_or_above(
        current_user_id, server_id
    ):
        raise ServerNotFoundError("Server not found or access denied")

    result = await connection_manager.execute_server_action(server_id, "stop")
    message: dict[str, str | bool] = {"success": result.success}
    if result.error:
        message["error"] = result.error

    return JSONResponse(content=message, status_code=result.status_code)


@server_router.post(
    "/{uuid}/restart", status_code=200, description="Перезапустить сервер."
)
async def restart_server(
    uuid: UUID,
    current_user_id: int = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service),
    connection_manager: ConnectionManager = Depends(get_connection_manager),
) -> JSONResponse:
    server_id = await server_service.get_server_id(uuid)
    if not server_id or not await server_service.is_admin_or_above(
        current_user_id, server_id
    ):
        raise ServerNotFoundError("Server not found or access denied")

    result = await connection_manager.execute_server_action(server_id, "restart")
    message: dict[str, str | bool] = {"success": result.success}
    if result.error:
        message["error"] = result.error

    return JSONResponse(content=message, status_code=result.status_code)


@server_router.post(
    "/{uuid}/command", status_code=200, description="Выполнить команду на сервере."
)
async def execute_command(
    uuid: UUID,
    command: str,
    current_user_id: int = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service),
    connection_manager: ConnectionManager = Depends(get_connection_manager),
) -> JSONResponse:
    server_id = await server_service.get_server_id(uuid)
    if not server_id or not await server_service.is_admin_or_above(
        current_user_id, server_id
    ):
        raise ServerNotFoundError("Server not found or access denied")

    result = await connection_manager.execute_server_command(server_id, command)
    message: dict[str, str | bool] = {"success": result.success}
    if result.error:
        message["error"] = result.error

    return JSONResponse(content=message, status_code=result.status_code)


@server_router.get(
    "/{uuid}/files",
    status_code=200,
    description="Получить файлы в папке сервера по пути.",
)
async def get_server_files(
    uuid: UUID,
    path: str | None = None,
    current_user_id: int = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service),
    connection_manager: ConnectionManager = Depends(get_connection_manager),
) -> JSONResponse:
    server_id = await server_service.get_server_id(uuid)
    if not server_id or not await server_service.is_admin_or_above(
        current_user_id, server_id
    ):
        raise ServerNotFoundError("Server not found or access denied")

    result = await connection_manager.get_server_item(server_id, path)
    message: dict[str, str | bool] = {"success": result.success}
    if result.error:
        message["error"] = result.error
    if result.data:
        message["item"] = result.data

    return JSONResponse(content=message, status_code=result.status_code)


@server_router.post(
    "/{uuid}/files",
    status_code=201,
    description="Создать файл/папку в папке сервера по пути.",
)
async def create_file(
    uuid: UUID,
    file: FileCreateRequest,
    current_user_id: int = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service),
    connection_manager: ConnectionManager = Depends(get_connection_manager),
) -> JSONResponse:
    server_id = await server_service.get_server_id(uuid)
    if not server_id or not await server_service.is_admin_or_above(
        current_user_id, server_id
    ):
        raise ServerNotFoundError("Server not found or access denied")

    result = await connection_manager.create_server_item(server_id, file)
    message: dict[str, str | bool] = {"success": result.success}
    if result.error:
        message["error"] = result.error

    return JSONResponse(content=message, status_code=result.status_code)


@server_router.put(
    "/{uuid}/files",
    status_code=200,
    description="Обновить файл/папку в папке сервера по пути.",
)
async def update_file(
    uuid: UUID,
    file: FileUpdateRequest,
    current_user_id: int = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service),
    connection_manager: ConnectionManager = Depends(get_connection_manager),
) -> JSONResponse:
    server_id = await server_service.get_server_id(uuid)
    if not server_id or not await server_service.is_admin_or_above(
        current_user_id, server_id
    ):
        raise ServerNotFoundError("Server not found or access denied")

    result = await connection_manager.update_server_item(server_id, file)
    message: dict[str, str | bool] = {"success": result.success}
    if result.error:
        message["error"] = result.error

    return JSONResponse(content=message, status_code=result.status_code)


@server_router.delete(
    "/{uuid}/files",
    status_code=200,
    description="Удалить файл/папку в папке сервера по пути.",
)
async def delete_file(
    uuid: UUID,
    path: str,
    current_user_id: int = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service),
    connection_manager: ConnectionManager = Depends(get_connection_manager),
) -> JSONResponse:
    server_id = await server_service.get_server_id(uuid)
    if not server_id or not await server_service.is_admin_or_above(
        current_user_id, server_id
    ):
        raise ServerNotFoundError("Server not found or access denied")

    result = await connection_manager.delete_server_file(server_id, path)
    message: dict[str, str | bool] = {"success": result.success}
    if result.error:
        message["error"] = result.error

    return JSONResponse(content=message, status_code=result.status_code)


@server_router.get(
    "/{uuid}/properties",
    status_code=200,
    description="Получить настройки сервера.",
)
async def get_settings(
    uuid: UUID,
    current_user_id: int = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service),
    connection_manager: ConnectionManager = Depends(get_connection_manager),
) -> JSONResponse:
    server_id = await server_service.get_server_id(uuid)
    if not server_id or not await server_service.is_admin_or_above(
        current_user_id, server_id
    ):
        raise ServerNotFoundError("Server not found or access denied")

    result = await connection_manager.get_server_settings(server_id)
    message: dict[str, str | bool] = {"success": result.success}
    if result.error:
        message["error"] = result.error
    if result.data:
        message["properties"] = result.data

    return JSONResponse(content=message, status_code=result.status_code)


@server_router.put(
    "/{uuid}/properties",
    status_code=200,
    description="Обновить значение настройки сервера.",
)
async def set_property(
    uuid: UUID,
    property: str,
    new_value: str,
    current_user_id: int = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service),
    connection_manager: ConnectionManager = Depends(get_connection_manager),
) -> JSONResponse:
    server_id = await server_service.get_server_id(uuid)
    if not server_id or not await server_service.is_admin_or_above(
        current_user_id, server_id
    ):
        raise ServerNotFoundError("Server not found or access denied")

    result = await connection_manager.set_server_setting(server_id, property, new_value)
    message: dict[str, str | bool] = {"success": result.success}
    if result.error:
        message["error"] = result.error

    return JSONResponse(content=message, status_code=result.status_code)
