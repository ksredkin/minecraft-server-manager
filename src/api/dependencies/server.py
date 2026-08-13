from src.api.dependencies.database import get_server_repository
from src.common.repositories.server_repository import ServerRepository
from fastapi import Depends
from src.api.services.server_service import ServerService
from src.api.services.key_service import KeyService

def get_key_service():
    return KeyService()

def get_server_service(server_repository: ServerRepository = Depends(get_server_repository), key_service: KeyService = Depends(get_key_service)):
    return ServerService(server_repository, key_service)
