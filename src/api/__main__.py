from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from src.common.core.config import API_HOST, API_PORT
from src.api.services.process_service import ProcessService
from src.api.services.properties_service import PropertiesService
from src.api.services.plugins_service import PluginsService
from src.api.services.eula_service import EulaService
from src.api.services.backup_service import BackupService

app = FastAPI(title="Minecraft Server Manager", description="API для управления Minecraft сервером.")
process_service = ProcessService()
properties_service = PropertiesService()
plugins_service = PluginsService()
eula_service = EulaService()
backup_service = BackupService()

@app.post("/start", description="Запустить сервер.")
def start() -> JSONResponse:
    success = process_service.start()
    if success:
        return JSONResponse({"success": True}, 200)
    else:
        raise HTTPException(500, {"success": False})

@app.post("/stop", description="Остановить сервер.")
def stop() -> JSONResponse:
    success = process_service.stop()
    if success:
        return JSONResponse({"success": True}, 200)
    else:
        raise HTTPException(500, {"success": False})

@app.post("/restart", description="Перезапустить сервер.")
def restart() -> JSONResponse:
    success = process_service.restart()
    if success:
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
    
@app.get("/plugins", description="Получить список всех плагинов сервера.")
def plugins() -> JSONResponse:
    plugins = plugins_service.get_plugins()
    if plugins is not None:
        return JSONResponse({"success": True, "data": {"plugins": plugins}}, 200)
    else:
        raise HTTPException(500, {"success": False})
    
@app.get("/eula", description="Получить текущий статус EULA.")
def get_eula() -> JSONResponse:
    status = eula_service.get_eula_status()
    if status is not None:
        return JSONResponse({"success": True, "data": {"eula": status}}, 200)
    else:
        raise HTTPException(500, {"success": False})

@app.post("/eula", description="Принять или отклонить EULA.")
def set_eula(accept_eula: bool = True) -> JSONResponse:
    success = eula_service.set_eula_status(accept_eula)
    if success:
        return JSONResponse({"success": True, "data": {"eula": accept_eula}}, 200)
    else:
        raise HTTPException(500, {"success": False})

@app.post("/command", description="Выполнить команду.")
def command(command: str) -> JSONResponse:
    success = process_service.execute_command(command)
    if success:
        return JSONResponse({"success": True}, 200)
    else:
        raise HTTPException(500, {"success": False})

@app.get("/backups", description="Просмотреть список резервных копий.")
def get_backups() -> JSONResponse:
    backups = backup_service.get_backups()
    if backups is not None:
        return JSONResponse({"success": True, "data": {"backups": backups}}, 201)
    else:
        raise HTTPException(500, {"success": False})

@app.post("/backups", description="Создать резервную копию сервера.")
def create_backup() -> JSONResponse:
    backup_name = backup_service.create_backup()
    return JSONResponse({"success": True, "data": {"name": backup_name}}, 201)

if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT)
