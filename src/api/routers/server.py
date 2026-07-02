from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.api.services.process_service import ProcessService, get_process_service

server_router = APIRouter()


@server_router.post("/start", description="Запустить сервер.")
def start(
    process_service: ProcessService = Depends(get_process_service),
) -> JSONResponse:
    return JSONResponse({"success": process_service.start()}, 200)


@server_router.post("/stop", description="Остановить сервер.")
def stop(
    process_service: ProcessService = Depends(get_process_service),
) -> JSONResponse:
    return JSONResponse({"success": process_service.stop()}, 200)


@server_router.post("/restart", description="Перезапустить сервер.")
def restart(
    process_service: ProcessService = Depends(get_process_service),
) -> JSONResponse:
    return JSONResponse({"success": process_service.restart()}, 200)


@server_router.get("/status", description="Получить текущий статус работы сервера.")
def status(
    process_service: ProcessService = Depends(get_process_service),
) -> JSONResponse:
    return JSONResponse(
        {"success": True, "data": {"status": process_service.status()}}, 200
    )


@server_router.post("/command", description="Выполнить команду.")
def command(
    command: str, process_service: ProcessService = Depends(get_process_service)
) -> JSONResponse:
    return JSONResponse({"success": process_service.execute_command(command)}, 200)


@server_router.get("/logs", description="Получить все логи сервера.")
def get_logs(
    process_service: ProcessService = Depends(get_process_service),
) -> JSONResponse:
    return JSONResponse(
        {"success": True, "data": {"logs": process_service.get_logs()}}, 200
    )


@server_router.get(
    "/logs/tail", description="Получить последние N строк логов сервера."
)
def get_logs_tail(
    limit: int,
    process_service: ProcessService = Depends(get_process_service),
) -> JSONResponse:
    return JSONResponse(
        {
            "success": True,
            "data": {"logs": process_service.get_logs()[: -limit - 1 : -1]},
        },
        200,
    )


@server_router.get("/players", description="Получить список игроков.")
def get_players(
    process_service: ProcessService = Depends(get_process_service),
) -> JSONResponse:
    return JSONResponse(
        {"success": True, "data": {"players": process_service.get_players()}}, 200
    )


@server_router.get("/info", description="Получить информацию о сервере.")
def get_server_info(
    process_service: ProcessService = Depends(get_process_service),
) -> JSONResponse:
    return JSONResponse(
        {"success": True, "data": {"info": process_service.get_server_info()}}, 200
    )
