from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from src.api.dependencies.auth import get_current_user_id
from src.api.dependencies.server import get_server_service
from src.api.services.server_service import ServerService
from src.api.services.server_user_service import ServerUserService
from src.api.schemas.server import ServerInfoResponse, ServerDeletedResponse
from src.common.database.connection import get_db_session
from src.common.repositories.server_repository import ServerRepository
from src.common.repositories.server_user_repository import ServerUserRepository
from src.api.dependencies.server import get_key_service
from src.api.services.key_service import KeyService
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID


server_router = APIRouter(prefix="/servers")


@server_router.post("/", status_code=201, description="Создать сервер.")
async def create_server(display_name: str|None = None, current_user_id: int = Depends(get_current_user_id), server_service: ServerService = Depends(get_server_service)) -> JSONResponse:
    server_created = await server_service.create_server(current_user_id, display_name)
    return {
        "uuid": server_created.uuid,
        "display_name": display_name or str(server_created.uuid),
        "daemon_key": server_created.daemon_key,
        "created_at": server_created.created_at
    }

@server_router.delete("/{uuid}", response_model=ServerDeletedResponse, status_code=200, description="Удалить сервер.")
async def delete_server(uuid: UUID, current_user_id: int = Depends(get_current_user_id), server_service: ServerService = Depends(get_server_service)) -> JSONResponse:
    deleted = await server_service.delete_for_user(current_user_id, uuid)

    if not deleted:
        return JSONResponse(content={"success": False, "error": "Server not found or you don't have permission to delete it"})

    return deleted

@server_router.get("/", response_model=list[ServerInfoResponse], status_code=200, description="Получить список серверов пользователя.")
async def get_servers(current_user_id: int = Depends(get_current_user_id), server_service: ServerService = Depends(get_server_service)):
    user_servers = await server_service.get_by_user(current_user_id)
    return [ServerInfoResponse(**server) for server in user_servers]

