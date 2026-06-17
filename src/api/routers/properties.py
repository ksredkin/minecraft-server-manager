from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from src.api.services.properties_service import get_properties_service, PropertiesService

properties_router = APIRouter(prefix="/properties")

@properties_router.get("/", description="Получить настройки сервера.")
def properties(properties_service: PropertiesService = Depends(get_properties_service)) -> JSONResponse:
    properties = properties_service.get_properties()
    if properties:
        return JSONResponse({"success": True, "data": {"properties": properties}}, 200)
    else:
        raise HTTPException(500, {"success": False})

@properties_router.put("/{property}", description="Обновить настройку сервера.")
def update_property(property: str, value: str, properties_service: PropertiesService = Depends(get_properties_service)) -> JSONResponse:
    success = properties_service.update_property(property, value)
    if success:
        return JSONResponse({"success": True, "data": {property: value}}, 200)
    else:
        raise HTTPException(500, {"success": False})