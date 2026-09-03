import asyncio
from datetime import datetime
from typing import Any
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
from src.api.services.backup_manager import BackupManager, get_backup_manager
from src.api.services.connection_manager import (
    ConnectionManager,
    get_connection_manager,
)
from src.api.services.server_service import ServerService
from src.api.services.task_manager import TaskManager, get_task_manager
from src.common.database.models import Server
from src.common.enums import TaskStatus

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
    if not user_servers or not isinstance(user_servers, list):
        return []
    return [ServerInfoResponse.model_validate(server) for server in user_servers]


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
    message: dict[str, Any] = {"success": result.success}
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
    message: dict[str, Any] = {"success": result.success}
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


@server_router.get(
    "/{uuid}/eula",
    status_code=200,
    description="Получить статус EULA на сервере.",
)
async def get_eula(
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

    result = await connection_manager.get_server_eula(server_id)
    message: dict[str, Any] = {"success": result.success}
    if result.error:
        message["error"] = result.error
    if result.data:
        message["eula"] = result.data

    return JSONResponse(content=message, status_code=result.status_code)


@server_router.put(
    "/{uuid}/eula",
    status_code=200,
    description="Установить статус EULA на сервере.",
)
async def set_eula(
    uuid: UUID,
    accept: bool = True,
    current_user_id: int = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service),
    connection_manager: ConnectionManager = Depends(get_connection_manager),
) -> JSONResponse:
    server_id = await server_service.get_server_id(uuid)
    if not server_id or not await server_service.is_admin_or_above(
        current_user_id, server_id
    ):
        raise ServerNotFoundError("Server not found or access denied")

    result = await connection_manager.set_server_eula(server_id, accept)
    message: dict[str, str | bool] = {"success": result.success}
    if result.error:
        message["error"] = result.error

    return JSONResponse(content=message, status_code=result.status_code)


@server_router.get(
    "/{uuid}/backups",
    status_code=200,
    description="Получить бэкапы сервера.",
)
async def get_server_backups(
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

    result = await connection_manager.get_server_backups(server_id)
    message: dict[str, Any] = {"success": result.success}
    if result.error:
        message["error"] = result.error
    if result.data:
        message["backups"] = result.data

    return JSONResponse(content=message, status_code=result.status_code)


@server_router.post(
    "/{uuid}/backups",
    status_code=202,
    description="Создать бэкап сервера.",
)
async def create_server_backup(
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

    result = await connection_manager.create_server_backup(server_id)
    message: dict[str, str | bool] = {"success": result.accepted}
    if result.error:
        message["error"] = result.error
    if result.data and isinstance(result.data, dict):
        message["task_id"] = str(result.data.get("task_id"))

    return JSONResponse(content=message, status_code=result.status_code)


@server_router.delete(
    "/{uuid}/backups/{backup}",
    status_code=200,
    description="Удалить бэкап сервера.",
)
async def delete_server_backup(
    uuid: UUID,
    backup: str,
    current_user_id: int = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service),
    connection_manager: ConnectionManager = Depends(get_connection_manager),
) -> JSONResponse:
    server_id = await server_service.get_server_id(uuid)
    if not server_id or not await server_service.is_admin_or_above(
        current_user_id, server_id
    ):
        raise ServerNotFoundError("Server not found or access denied")

    result = await connection_manager.delete_server_backup(server_id, backup)
    message: dict[str, str | bool] = {"success": result.success}
    if result.error:
        message["error"] = result.error

    return JSONResponse(content=message, status_code=result.status_code)


@server_router.post(
    "/{uuid}/backups/{backup}/restore",
    status_code=200,
    description="Восстановить сервер по бэкапу.",
)
async def restore_server_backup(
    uuid: UUID,
    backup: str,
    current_user_id: int = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service),
    connection_manager: ConnectionManager = Depends(get_connection_manager),
) -> JSONResponse:
    server_id = await server_service.get_server_id(uuid)
    if not server_id or not await server_service.is_admin_or_above(
        current_user_id, server_id
    ):
        raise ServerNotFoundError("Server not found or access denied")

    result = await connection_manager.restore_server_backup(server_id, backup)
    message: dict[str, str | bool] = {"success": result.accepted}
    if result.error:
        message["error"] = result.error
    if result.data and isinstance(result.data, dict):
        message["task_id"] = str(result.data.get("task_id"))

    return JSONResponse(content=message, status_code=result.status_code)


@server_router.get(
    "/{uuid}/backups/cloud",
    status_code=200,
    description="Получить облачные бэкапы сервера.",
)
async def get_server_cloud_backups(
    uuid: UUID,
    current_user_id: int = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service),
    backup_manager: BackupManager = Depends(get_backup_manager),
) -> JSONResponse:
    server_id = await server_service.get_server_id(uuid)
    if not server_id or not await server_service.is_admin_or_above(
        current_user_id, server_id
    ):
        raise ServerNotFoundError("Server not found or access denied")

    backups = backup_manager.get_server_backups(server_id)
    message: dict[str, bool | list[dict[str, str | int]]] = {
        "success": True,
        "backups": [{"name": backup.name, "size": backup.size} for backup in backups],
    }
    return JSONResponse(content=message)


@server_router.get(
    "/{uuid}/backups/cloud/status",
    status_code=200,
    description="Получить статус облачного пространства.",
)
async def get_server_cloud_status(
    uuid: UUID,
    current_user_id: int = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service),
    backup_manager: BackupManager = Depends(get_backup_manager),
) -> JSONResponse:
    server_id = await server_service.get_server_id(uuid)
    if not server_id or not await server_service.is_admin_or_above(
        current_user_id, server_id
    ):
        raise ServerNotFoundError("Server not found or access denied")

    status = await backup_manager.get_server_cloud_status(server_id)
    message: dict[str, bool | int] = {"success": True, **status}
    return JSONResponse(content=message)


@server_router.delete(
    "/{uuid}/backups/cloud/{backup}",
    status_code=200,
    description="Удалить бэкап в облачном пространстве.",
)
async def delete_server_cloud_backup(
    uuid: UUID,
    backup: str,
    current_user_id: int = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service),
    backup_manager: BackupManager = Depends(get_backup_manager),
) -> JSONResponse:
    server_id = await server_service.get_server_id(uuid)
    if not server_id or not await server_service.is_admin_or_above(
        current_user_id, server_id
    ):
        raise ServerNotFoundError("Server not found or access denied")

    await backup_manager.delete_backup(server_id, backup)
    message: dict[str, bool | str] = {"success": True, "backup": backup}
    return JSONResponse(content=message)


@server_router.post(
    "/{uuid}/backups/{backup}/cloud",
    description="Отправить бэкап сервера в облако.",
)
async def upload_server_backup_to_cloud(
    uuid: UUID,
    backup: str,
    current_user_id: int = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service),
    connection_manager: ConnectionManager = Depends(get_connection_manager),
) -> JSONResponse:
    server_id = await server_service.get_server_id(uuid)
    if not server_id or not await server_service.is_admin_or_above(
        current_user_id, server_id
    ):
        raise ServerNotFoundError("Server not found or access denied")

    result = await connection_manager.upload_server_backup_to_cloud(server_id, backup)
    message: dict[str, str | bool] = {"success": result.accepted}
    if result.error:
        message["error"] = result.error
    if result.data and isinstance(result.data, dict):
        message["task_id"] = str(result.data.get("task_id"))

    return JSONResponse(content=message, status_code=result.status_code)


@server_router.post(
    "/{uuid}/backups/cloud/{backup}/download",
    description="Скачать бэкап с облака на сервер.",
)
async def download_server_backup_from_cloud(
    uuid: UUID,
    backup: str,
    current_user_id: int = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service),
    connection_manager: ConnectionManager = Depends(get_connection_manager),
) -> JSONResponse:
    server_id = await server_service.get_server_id(uuid)
    if not server_id or not await server_service.is_admin_or_above(
        current_user_id, server_id
    ):
        raise ServerNotFoundError("Server not found or access denied")

    result = await connection_manager.download_server_backup_from_cloud(
        server_id, backup
    )
    message: dict[str, str | bool] = {"success": result.accepted}
    if result.error:
        message["error"] = result.error
    if result.data and isinstance(result.data, dict):
        message["task_id"] = str(result.data.get("task_id"))

    return JSONResponse(content=message, status_code=result.status_code)


@server_router.get(
    "/{uuid}/backups/tasks/{task_id}",
    status_code=200,
    description="Получить статус задачи бэкапа сервера и удалить задачу, если есть результат.",
)
async def get_server_backup_task(
    uuid: UUID,
    task_id: UUID,
    current_user_id: int = Depends(get_current_user_id),
    server_service: ServerService = Depends(get_server_service),
    task_manager: TaskManager = Depends(get_task_manager),
) -> JSONResponse:
    server_id = await server_service.get_server_id(uuid)
    if not server_id or not await server_service.is_admin_or_above(
        current_user_id, server_id
    ):
        raise ServerNotFoundError("Server not found or access denied")

    status = task_manager.get_task_status(server_id, task_id)
    if status is None or not isinstance(status, TaskStatus):
        return JSONResponse(
            content={"success": False, "error": "Task not found or access denied"},
            status_code=404,
        )

    task = {}
    if status == TaskStatus.FAILED or status == TaskStatus.COMPLETED:
        task_result = await task_manager.get_result(server_id, task_id)
        if not task_result or not isinstance(task_result, dict):
            return JSONResponse(
                content={"success": False, "error": "Task not found or access denied"},
                status_code=404,
            )

        if task_result.get("success") is not None:
            task["success"] = task_result.get("success")
        if task_result.get("error") is not None:
            task["error"] = task_result.get("error")

        await task_manager.remove(server_id, task_id)

    if status == TaskStatus.ACCEPTED:
        completion_percent = task_manager.get_task_completion_percent(
            server_id, task_id
        )
        task["completion_percent"] = completion_percent

    task["status"] = str(status.value)

    return JSONResponse(content={"success": True, "task": task}, status_code=200)
