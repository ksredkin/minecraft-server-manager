from fastapi import APIRouter
from src.api.schemas.plugin import plugin_provider
from src.api.services.plugin_service import PluginService
from fastapi.responses import JSONResponse
from src.api.dependencies.plugin import get_plugin_service

plugin_router = APIRouter(prefix="/plugins")


@plugin_router.get("/{provider}/{project_id_or_slug}")
async def get_plugin_info(
    project_id_or_slug: str,
    provider: plugin_provider = "modrinth",
) -> JSONResponse:
    plugin_service = get_plugin_service(provider)
    result = await plugin_service.get_plugin_info(project_id_or_slug)
    return JSONResponse(content={"success": True, "info": result})