from src.api.dependencies.database import get_server_user_repository
from src.common.repositories.server_user_repository import ServerUserRepository
from fastapi import Depends
from src.api.services.server_user_service import ServerUserService

def get_server_user_service(server_repository: ServerUserRepository = Depends(get_server_user_repository)):
    return ServerUserService(server_repository)
