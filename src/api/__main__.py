import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.routers.backups import backups_router
from src.api.routers.eula import eula_router
from src.api.routers.plugins import plugins_router
from src.api.routers.properties import properties_router
from src.api.routers.server import server_router
from src.common.core.config import API_HOST, API_PORT
from src.common.exceptions import (
    InvalidServerConfigurationError,
    MSMError,
    ServerAlreadyRunningError,
    ServerFolderDoesNotExistError,
    ServerNotRunningError,
    ServerResponseTimeoutError,
    ServerStopTimeoutError,
)

app = FastAPI(
    title="Minecraft Server Manager",
    description="API для управления Minecraft сервером.",
)


ERRORS = {
    ServerAlreadyRunningError: 409,
    ServerNotRunningError: 409,
    InvalidServerConfigurationError: 500,
    ServerFolderDoesNotExistError: 404,
    ServerStopTimeoutError: 500,
    ServerResponseTimeoutError: 500,
}


@app.exception_handler(MSMError)
async def handler(request: Request, exc: MSMError) -> JSONResponse:
    status = ERRORS[type(exc)]
    return JSONResponse(
        status_code=status,
        content={
            "success": False,
            "error": str(exc),
        },
    )


def main() -> None:
    app.include_router(server_router)
    app.include_router(backups_router)
    app.include_router(eula_router)
    app.include_router(plugins_router)
    app.include_router(properties_router)

    uvicorn.run(app, host=API_HOST, port=API_PORT)


if __name__ == "__main__":
    main()
