from src.api.dependencies.database import get_daemon_key_repository
from src.common.repositories.daemon_key_repository import DaemonKeyRepository
from src.api.services.daemon_key_service import DaemonKeyService
from fastapi import Depends
from src.api.services.key_service import KeyService

def get_key_service():
    return KeyService()

def get_daemon_key_service(daemon_key_repository: DaemonKeyRepository = Depends(get_daemon_key_repository), key_service: KeyService = Depends(get_key_service)) -> DaemonKeyService:
    return DaemonKeyService(daemon_key_repository, key_service)
