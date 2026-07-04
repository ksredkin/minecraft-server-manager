from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.api.services.plugins_service import PluginsService, get_plugins_service
from src.common.utils.logger import Logger

logger = Logger(__name__)
plugins_router = APIRouter(prefix="/plugins")


@plugins_router.get("/", description="Получить список всех плагинов сервера.")
def plugins(
    plugins_service: PluginsService = Depends(get_plugins_service),
) -> JSONResponse:
    plugins = plugins_service.get_plugins()
    return JSONResponse({"success": True, "data": {"plugins": plugins}}, 200)


@plugins_router.get("/search", description="Найти плагины.")
async def search_plugins(
    query: str,
    plugins_service: PluginsService = Depends(get_plugins_service),
) -> JSONResponse:
    result = await plugins_service.search_plugins(query)
    return JSONResponse({"success": True, "data": {"plugins": result}}, 200)


@plugins_router.get("/info", description="Получить информацию о плагине.")
async def get_plugin_info(
    project_id_or_slug: str,
    plugins_service: PluginsService = Depends(get_plugins_service),
) -> JSONResponse:
    result = await plugins_service.get_plugin_info(project_id_or_slug)
    return JSONResponse({"success": True, "data": {project_id_or_slug: result}}, 200)


@plugins_router.post("/install/{project_id_or_slug}", description="Скачать плагин.")
async def install_plugin(
    project_id_or_slug: str,
    plugins_service: PluginsService = Depends(get_plugins_service),
) -> JSONResponse:
    result = await plugins_service.install_plugin(project_id_or_slug)
    logger.info(f"Успешно установлен плагин: {project_id_or_slug}")
    return JSONResponse({"success": True, "data": {project_id_or_slug: result}}, 201)


@plugins_router.delete(
    "/delete/{jar_name_without_extension}", description="Удалить плагин."
)
def delete_plugin(
    jar_name_without_extension: str,
    plugins_service: PluginsService = Depends(get_plugins_service),
) -> JSONResponse:
    plugin = plugins_service.delete_plugin(jar_name_without_extension)
    logger.info(f"Успешно удален плагин: {plugin}")
    return JSONResponse({"success": True, "data": {"plugin": plugin}}, 200)
