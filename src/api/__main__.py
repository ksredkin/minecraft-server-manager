from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from src.common.core.config import API_HOST, API_PORT
from src.api.services.process_service import ProcessService
from src.api.services.properties_service import PropertiesService

app = FastAPI(title="Minecraft Server Manager", description="API для управления Minecraft сервером.")
process_service = ProcessService()
properties_service = PropertiesService()

@app.post("/start", description="Запустить сервер.")
def start() -> JSONResponse:
    result = process_service.start()
    if result:
        return JSONResponse({"success": True}, 200)
    else:
        raise HTTPException(500, {"success": False})

@app.post("/stop", description="Остановить сервер.")
def stop() -> JSONResponse:
    result = process_service.stop()
    if result:
        return JSONResponse({"success": True}, 200)
    else:
        raise HTTPException(500, {"success": False})

@app.post("/restart", description="Перезапустить сервер.")
def restart() -> JSONResponse:
    result = process_service.restart()
    if result:
        return JSONResponse({"success": True}, 200)
    else:
        raise HTTPException(500, {"success": False})

@app.get("/status", description="Получить текущий статус работы сервера.")
def status() -> JSONResponse:
    status = process_service.status()
    if status:
        return JSONResponse({"success": True, "data": {"status": status}}, 200)
    else:
        raise HTTPException(500, {"success": False})
    
@app.get("/properties", description="Получить настройки сервера.")
def properties() -> JSONResponse:
    properties = properties_service.get_properties()
    if properties:
        return JSONResponse({"success": True, "data": {"properties": properties}}, 200)
    else:
        raise HTTPException(500, {"success": False})

@app.put("/properties/{property}", description="Обновить настройку сервера.")
def update_property(property: str, value: str) -> JSONResponse:
    success = properties_service.update_property(property, value)
    if success:
        return JSONResponse({"success": True, "data": {property: value}}, 200)
    else:
        raise HTTPException(500, {"success": False})

if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT)
