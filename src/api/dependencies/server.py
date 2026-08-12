from src.api.dependencies.database import get_server_repository
from src.common.repositories.server_repository import ServerRepository
from fastapi import Depends
from src.api.services.server_service import ServerService

def get_server_service(server_repository: ServerRepository = Depends(get_server_repository)):
    return ServerService(server_repository)
