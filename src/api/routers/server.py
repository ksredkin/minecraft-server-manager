from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from src.api.dependencies.auth import get_current_user_id
from src.api.dependencies.server import get_server_service
from src.api.dependencies.server_user import get_server_user_service
from src.api.services.server_service import ServerService
from src.api.services.server_user_service import ServerUserService
from src.api.schemas.server import ServerResponse


server_router = APIRouter(prefix="/server")


@server_router.post("/", response_model=ServerResponse, status_code=201)
async def create_server(display_name: str|None = None, current_user_id: int = Depends(get_current_user_id), server_service: ServerService = Depends(get_server_service), server_users_service: ServerUserService = Depends(get_server_user_service)) -> JSONResponse:
    server = await server_service.create_server()
    await server_users_service.create_server_user(server.id, current_user_id, display_name or str(server.uuid), "owner")
    return server
