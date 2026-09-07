from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.exceptions.api import MSMAPIError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(MSMAPIError)
    def handler(request: Request, exc: MSMAPIError) -> JSONResponse:
        return JSONResponse(
            content={"success": False, "error": str(exc)},
            status_code=exc.status_code,
        )
