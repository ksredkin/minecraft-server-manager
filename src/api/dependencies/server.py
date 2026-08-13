from src.common.repositories.server_repository import ServerRepository
from src.common.repositories.server_user_repository import ServerUserRepository
from fastapi import Depends
from src.api.services.server_service import ServerService
from src.api.services.key_service import KeyService
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.database.connection import get_db_session
from src.api.services.server_user_service import ServerUserService

def get_key_service():
    return KeyService()

def get_server_service(session: AsyncSession = Depends(get_db_session), key_service: KeyService = Depends(get_key_service)):
    return ServerService(ServerRepository(session), key_service, ServerUserService(ServerUserRepository(session)))
