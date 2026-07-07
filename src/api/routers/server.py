import asyncio

from fastapi import APIRouter, Depends, WebSocket
from fastapi.responses import JSONResponse

from src.api.services.connection_manager import (
    ConnectionManager,
    get_connection_manager,
)
from src.api.services.process_service import ProcessService, get_process_service
from src.common.utils.logger import Logger

server_router = APIRouter()
logger = Logger(__name__)


@server_router.post("/start", description="Запустить сервер.")
def start(
    process_service: ProcessService = Depends(get_process_service),
) -> JSONResponse:
    started = process_service.start()
    logger.info("Сервер успешно запущен.")
    return JSONResponse({"success": started}, 200)


@server_router.post("/stop", description="Остановить сервер.")
def stop(
    process_service: ProcessService = Depends(get_process_service),
) -> JSONResponse:
    process_service.stop()
    logger.info("Сервер успешно остановлен.")
    return JSONResponse({"success": True}, 200)


@server_router.post("/restart", description="Перезапустить сервер.")
def restart(
    process_service: ProcessService = Depends(get_process_service),
) -> JSONResponse:
    restarted = process_service.restart()
    logger.info("Сервер успешно перезапущен.")
    return JSONResponse({"success": restarted}, 200)


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
    process_service.execute_command(command)
    logger.info(f"Успешно выполнена команда: {command}")
    return JSONResponse({"success": True}, 200)


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


@server_router.websocket("/ws/logs")
async def logs_websocket(
    websocket: WebSocket,
    connection_manager: ConnectionManager = Depends(get_connection_manager),
) -> None:
    await connection_manager.connect(websocket)

    while True:
        await asyncio.sleep(1)


@server_router.get("/players", description="Получить список игроков.")
def get_players(
    process_service: ProcessService = Depends(get_process_service),
) -> JSONResponse:
    players = process_service.get_players()
    return JSONResponse({"success": True, "data": {"players": players}}, 200)


@server_router.get("/info", description="Получить информацию о сервере.")
def get_server_info(
    process_service: ProcessService = Depends(get_process_service),
) -> JSONResponse:
    info = process_service.get_server_info()
    return JSONResponse({"success": True, "data": {"info": info}}, 200)
