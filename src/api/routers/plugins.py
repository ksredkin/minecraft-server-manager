import httpx
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.api.services.plugins_service import PluginsService, get_plugins_service

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
    try:
        result = await plugins_service.search_plugins(query)
        return JSONResponse({"success": True, "data": {"plugins": result}}, 200)
    except httpx.TimeoutException:
        return JSONResponse(
            {
                "success": False,
                "error": "Timeout при подключении к API Modrinth. Попробуйте позже.",
            },
            504,
        )
    except httpx.ConnectError:
        return JSONResponse(
            {
                "success": False,
                "error": "Не удалось подключиться к API Modrinth. Проверьте соединение.",
            },
            503,
        )
    except httpx.NetworkError:
        return JSONResponse(
            {
                "success": False,
                "error": "Сетевая ошибка при подключении к API Modrinth.",
            },
            503,
        )
    except httpx.ProtocolError:
        return JSONResponse(
            {
                "success": False,
                "error": "Ошибка протокола при подключении к API Modrinth.",
            },
            502,
        )
    except httpx.HTTPError as e:
        return JSONResponse(
            {
                "success": False,
                "error": f"Ошибка HTTP при подключении к API: {str(e)}",
            },
            500,
        )


@plugins_router.get("/info", description="Получить информацию о плагине.")
async def get_plugin_info(
    project_id_or_slug: str,
    plugins_service: PluginsService = Depends(get_plugins_service),
) -> JSONResponse:
    try:
        result = await plugins_service.get_plugin_info(project_id_or_slug)
        return JSONResponse(
            {"success": True, "data": {project_id_or_slug: result}}, 200
        )
    except httpx.TimeoutException:
        return JSONResponse(
            {
                "success": False,
                "error": "Timeout при получении информации о плагине. Попробуйте позже.",
            },
            504,
        )
    except httpx.ConnectError:
        return JSONResponse(
            {
                "success": False,
                "error": "Не удалось подключиться к API Modrinth. Проверьте соединение.",
            },
            503,
        )
    except httpx.NetworkError:
        return JSONResponse(
            {
                "success": False,
                "error": "Сетевая ошибка при получении информации о плагине.",
            },
            503,
        )
    except httpx.ProtocolError:
        return JSONResponse(
            {
                "success": False,
                "error": "Ошибка протокола при получении информации о плагине.",
            },
            502,
        )
    except httpx.HTTPError as e:
        return JSONResponse(
            {
                "success": False,
                "error": f"Ошибка HTTP при получении информации: {str(e)}",
            },
            500,
        )


@plugins_router.post("/install/{project_id_or_slug}", description="Скачать плагин.")
async def install_plugin(
    project_id_or_slug: str,
    plugins_service: PluginsService = Depends(get_plugins_service),
) -> JSONResponse:
    try:
        result = await plugins_service.install_plugin(project_id_or_slug)
        return JSONResponse(
            {"success": True, "data": {project_id_or_slug: result}}, 201
        )
    except httpx.TimeoutException:
        return JSONResponse(
            {
                "success": False,
                "error": "Timeout при загрузке плагина. Попробуйте позже.",
            },
            504,
        )
    except httpx.ConnectError:
        return JSONResponse(
            {
                "success": False,
                "error": "Не удалось подключиться к API Modrinth. Проверьте соединение.",
            },
            503,
        )
    except httpx.NetworkError:
        return JSONResponse(
            {
                "success": False,
                "error": "Сетевая ошибка при загрузке плагина.",
            },
            503,
        )
    except httpx.ProtocolError:
        return JSONResponse(
            {
                "success": False,
                "error": "Ошибка протокола при загрузке плагина.",
            },
            502,
        )
    except httpx.HTTPError as e:
        return JSONResponse(
            {
                "success": False,
                "error": f"Ошибка HTTP при загрузке плагина: {str(e)}",
            },
            500,
        )
