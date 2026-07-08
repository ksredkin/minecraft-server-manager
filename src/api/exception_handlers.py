from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.exceptions.api_client import (
    ApiClientConnectionError,
    ApiClientHttpError,
    ApiClientInvalidResponseError,
    ApiClientNetworkError,
    ApiClientProtocolError,
    ApiClientTimeoutError,
)
from src.api.exceptions.eula import (
    EulaFileNotFoundError,
    EulaStatusNotFoundError,
)
from src.api.exceptions.plugins import (
    PluginJarNotFoundError,
    PluginsFolderDoesNotExistError,
    PluginVersionNotFoundError,
)
from src.api.exceptions.server import (
    InvalidServerConfigurationError,
    MSMError,
    ServerAlreadyRunningError,
    ServerFolderDoesNotExistError,
    ServerNotRunningError,
    ServerResponseTimeoutError,
    ServerStopTimeoutError,
)
from src.api.exceptions.settings import SettingsFileNotFoundError

ERRORS = {
    # Server
    ServerAlreadyRunningError: 409,
    ServerNotRunningError: 409,
    InvalidServerConfigurationError: 500,
    ServerFolderDoesNotExistError: 404,
    ServerStopTimeoutError: 504,
    ServerResponseTimeoutError: 504,
    # API Client
    ApiClientTimeoutError: 504,
    ApiClientConnectionError: 503,
    ApiClientNetworkError: 503,
    ApiClientProtocolError: 502,
    ApiClientHttpError: 502,
    ApiClientInvalidResponseError: 502,
    # Plugins
    PluginsFolderDoesNotExistError: 404,
    PluginJarNotFoundError: 404,
    PluginVersionNotFoundError: 404,
    # EULA
    EulaFileNotFoundError: 404,
    EulaStatusNotFoundError: 500,
    # Settings
    SettingsFileNotFoundError: 404,
}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(MSMError)
    async def handler(request: Request, exc: MSMError) -> JSONResponse:
        status = ERRORS.get(type(exc), 500)
        return JSONResponse(
            status_code=status,
            content={
                "success": False,
                "error": str(exc),
            },
        )
