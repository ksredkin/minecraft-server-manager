from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from src.api.dependencies.auth import get_current_user_id
from src.api.dependencies.server import get_server_service
from src.api.services.server_service import ServerService
from src.api.services.server_user_service import ServerUserService
from src.api.schemas.server import ServerInfoResponse
from src.common.database.connection import get_db_session
from src.common.repositories.server_repository import ServerRepository
from src.common.repositories.server_user_repository import ServerUserRepository
from src.api.dependencies.server import get_key_service
from src.api.services.key_service import KeyService
from sqlalchemy.ext.asyncio import AsyncSession


server_router = APIRouter(prefix="/servers")


@server_router.post("/", status_code=201, description="Создать сервер.")
async def create_server(display_name: str|None = None, current_user_id: int = Depends(get_current_user_id), key_service: KeyService = Depends(get_key_service), session: AsyncSession = Depends(get_db_session)) -> JSONResponse:
    server_service = ServerService(ServerRepository(session), key_service)
    server_users_service =  ServerUserService(ServerUserRepository(session))

    server_created = await server_service.create_server()
    await server_users_service.create_server_user(server_created.id, current_user_id, display_name or str(server_created.uuid), "owner")

    return {
        "uuid": server_created.uuid,
        "display_name": display_name or str(server_created.uuid),
        "daemon_key": server_created.daemon_key,
    }

@server_router.get("/", response_model=list[ServerInfoResponse], status_code=200, description="Получить список серверов пользователя.")
async def get_servers(current_user_id: int = Depends(get_current_user_id), server_service: ServerService = Depends(get_server_service)):
    user_servers = await server_service.get_by_user(current_user_id)
    return [ServerInfoResponse(**server) for server in user_servers]

