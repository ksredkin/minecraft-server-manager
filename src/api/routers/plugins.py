from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from src.api.services.plugins_service import PluginsService, get_plugins_service

plugins_router = APIRouter(prefix="/plugins")


@plugins_router.get("/", description="Получить список всех плагинов сервера.")
def plugins(
    plugins_service: PluginsService = Depends(get_plugins_service),
) -> JSONResponse:
    plugins = plugins_service.get_plugins()
    if plugins is not None:
        return JSONResponse({"success": True, "data": {"plugins": plugins}}, 200)
    else:
        raise HTTPException(500, {"success": False})
