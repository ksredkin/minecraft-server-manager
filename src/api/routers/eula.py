from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from src.api.services.eula_service import EulaService, get_eula_service

eula_router = APIRouter(prefix="/eula")


@eula_router.get("/", description="Получить текущий статус EULA.")
def get_eula(eula_service: EulaService = Depends(get_eula_service)) -> JSONResponse:
    status = eula_service.get_eula_status()
    if status is not None:
        return JSONResponse({"success": True, "data": {"eula": status}}, 200)
    else:
        raise HTTPException(500, {"success": False})


@eula_router.post("/", description="Принять или отклонить EULA.")
def set_eula(
    accept_eula: bool = True, eula_service: EulaService = Depends(get_eula_service)
) -> JSONResponse:
    success = eula_service.set_eula_status(accept_eula)
    if success:
        return JSONResponse({"success": True, "data": {"eula": accept_eula}}, 200)
    else:
        raise HTTPException(500, {"success": False})
