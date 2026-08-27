from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.exceptions.api import MSMAPIError
from src.api.exceptions.daemon import (
    DaemonDisconnectedError,
    InvalidDaemonResponseError,
)
from src.api.exceptions.billing import NewPlanIsLowerThanCurrent, PlanAlreadyActive, ActiveSubscriptionNotFound
from src.api.exceptions.server import ServerNotFoundError

ERRORS = {
    ServerNotFoundError: 404,
    DaemonDisconnectedError: 503,
    InvalidDaemonResponseError: 500,
    NewPlanIsLowerThanCurrent: 400,
    PlanAlreadyActive: 400,
    ActiveSubscriptionNotFound: 500
}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(MSMAPIError)
    def handler(request: Request, exc: MSMAPIError) -> JSONResponse:
        status_code = ERRORS.get(type(exc), 500)
        return JSONResponse(
            content={"success": False, "error": str(exc)}, status_code=status_code
        )
