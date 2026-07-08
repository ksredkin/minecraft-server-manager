from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.api.services.eula_service import EulaService, get_eula_service
from src.api.utils.logger import Logger

logger = Logger(__name__)
eula_router = APIRouter(prefix="/eula")


@eula_router.get("/", description="Получить текущий статус EULA.")
def get_eula(eula_service: EulaService = Depends(get_eula_service)) -> JSONResponse:
    status = eula_service.get_eula_status()
    return JSONResponse({"success": True, "data": {"eula": status}}, 200)


@eula_router.post("/", description="Принять или отклонить EULA.")
def set_eula(
    accept_eula: bool = True, eula_service: EulaService = Depends(get_eula_service)
) -> JSONResponse:
    eula_service.set_eula_status(accept_eula)
    logger.info(f"Пользователь {'принял' if accept_eula else 'отклонил'} EULA.")
    return JSONResponse({"success": True, "data": {"eula": accept_eula}}, 200)
