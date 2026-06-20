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


@plugins_router.get("/search", description="Найти плагины.")
async def search_plugins(
    query: str,
    plugins_service: PluginsService = Depends(get_plugins_service),
) -> JSONResponse:
    result = await plugins_service.search_plugins(query)
    if result is not None:
        return JSONResponse({"success": True, "data": {"plugins": result}}, 200)
    else:
        raise HTTPException(500, {"success": False})


@plugins_router.get("/info", description="Получить информацию о плагине.")
async def get_plugin_info(
    project_id_or_slug: str,
    plugins_service: PluginsService = Depends(get_plugins_service),
) -> JSONResponse:
    result = await plugins_service.get_plugin_info(project_id_or_slug)
    if result is not None:
        return JSONResponse(
            {"success": True, "data": {project_id_or_slug: result}}, 200
        )
    else:
        raise HTTPException(500, {"success": False})
