from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from src.api.services.process_service import get_process_service, ProcessService

server_router = APIRouter()

@server_router.post("/start", description="Запустить сервер.")
def start(process_service: ProcessService = Depends(get_process_service)) -> JSONResponse:
    success = process_service.start()
    if success:
        return JSONResponse({"success": True}, 200)
    else:
        raise HTTPException(500, {"success": False})

@server_router.post("/stop", description="Остановить сервер.")
def stop(process_service: ProcessService = Depends(get_process_service)) -> JSONResponse:
    success = process_service.stop()
    if success:
        return JSONResponse({"success": True}, 200)
    else:
        raise HTTPException(500, {"success": False})

@server_router.post("/restart", description="Перезапустить сервер.")
def restart(process_service: ProcessService = Depends(get_process_service)) -> JSONResponse:
    success = process_service.restart()
    if success:
        return JSONResponse({"success": True}, 200)
    else:
        raise HTTPException(500, {"success": False})

@server_router.get("/status", description="Получить текущий статус работы сервера.")
def status(process_service: ProcessService = Depends(get_process_service)) -> JSONResponse:
    status = process_service.status()
    if status:
        return JSONResponse({"success": True, "data": {"status": status}}, 200)
    else:
        raise HTTPException(500, {"success": False})

@server_router.post("/command", description="Выполнить команду.")
def command(command: str, process_service: ProcessService = Depends(get_process_service)) -> JSONResponse:
    success = process_service.execute_command(command)
    if success:
        return JSONResponse({"success": True}, 200)
    else:
        raise HTTPException(500, {"success": False})
