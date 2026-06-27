from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from src.api.services.process_service import ProcessService, get_process_service

server_router = APIRouter()


@server_router.post("/start", description="Запустить сервер.")
def start(
    process_service: ProcessService = Depends(get_process_service),
) -> JSONResponse:
    success = process_service.start()
    if success is not None:
        return JSONResponse({"success": True}, 200)
    else:
        raise HTTPException(500, {"success": False})


@server_router.post("/stop", description="Остановить сервер.")
def stop(
    process_service: ProcessService = Depends(get_process_service),
) -> JSONResponse:
    success = process_service.stop()
    if success is not None:
        return JSONResponse({"success": True}, 200)
    else:
        raise HTTPException(500, {"success": False})


@server_router.post("/restart", description="Перезапустить сервер.")
def restart(
    process_service: ProcessService = Depends(get_process_service),
) -> JSONResponse:
    success = process_service.restart()
    if success is not None:
        return JSONResponse({"success": True}, 200)
    else:
        raise HTTPException(500, {"success": False})


@server_router.get("/status", description="Получить текущий статус работы сервера.")
def status(
    process_service: ProcessService = Depends(get_process_service),
) -> JSONResponse:
    status = process_service.status()
    if status:
        return JSONResponse({"success": True, "data": {"status": status}}, 200)
    else:
        raise HTTPException(500, {"success": False})


@server_router.post("/command", description="Выполнить команду.")
def command(
    command: str, process_service: ProcessService = Depends(get_process_service)
) -> JSONResponse:
    success = process_service.execute_command(command)
    if success:
        return JSONResponse({"success": True}, 200)
    else:
        raise HTTPException(500, {"success": False})


@server_router.get("/logs", description="Получить все логи сервера.")
def get_logs(
    process_service: ProcessService = Depends(get_process_service),
) -> JSONResponse:
    logs = process_service.get_logs()
    if logs is not None:
        return JSONResponse({"success": True, "data": {"logs": logs}}, 200)
    else:
        raise HTTPException(500, {"success": False})


@server_router.get(
    "/logs/tail", description="Получить последние N строк логов сервера."
)
def get_logs_tail(
    limit: int,
    process_service: ProcessService = Depends(get_process_service),
) -> JSONResponse:
    logs = process_service.get_logs()
    if logs is not None:
        return JSONResponse(
            {"success": True, "data": {"logs": logs[: -limit - 1 : -1]}}, 200
        )
    else:
        raise HTTPException(500, {"success": False})


@server_router.get("/players", description="Получить список игроков.")
def get_players(
    process_service: ProcessService = Depends(get_process_service),
) -> JSONResponse:
    players = process_service.get_players()
    if players is not None:
        return JSONResponse({"success": True, "data": {"players": players}}, 200)
    else:
        raise HTTPException(500, {"success": False})
