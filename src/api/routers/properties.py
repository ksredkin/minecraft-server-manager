from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.api.services.properties_service import (
    PropertiesService,
    get_properties_service,
)
from src.api.utils.logger import Logger

logger = Logger(__name__)
properties_router = APIRouter(prefix="/properties")


@properties_router.get("/", description="Получить настройки сервера.")
def properties(
    properties_service: PropertiesService = Depends(get_properties_service),
) -> JSONResponse:
    properties = properties_service.get_properties()
    return JSONResponse({"success": True, "data": {"properties": properties}}, 200)


@properties_router.put("/{property}", description="Обновить настройку сервера.")
def update_property(
    property: str,
    value: str,
    properties_service: PropertiesService = Depends(get_properties_service),
) -> JSONResponse:
    properties_service.update_property(property, value)
    logger.info(f"Успешно обновлена настройка сервера: {property} = {value}")
    return JSONResponse({"success": True, "data": {property: value}}, 200)
