from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from src.api.dependencies.auth import get_auth_service, get_current_user_id
from src.api.services.auth_service import AuthService

auth_router = APIRouter(prefix="/auth")


@auth_router.post("/register")
async def register(
    login: str,
    password: str,
    email: str | None = None,
    auth_service: AuthService = Depends(get_auth_service),
) -> JSONResponse:
    token = await auth_service.register(login, password, email)

    if not token:
        return JSONResponse(
            content={"success": False, "error": "User already exists"}, status_code=409
        )

    return JSONResponse(
        content={"success": True, "access_token": token, "token_type": "Bearer"},
        status_code=201,
    )


@auth_router.post("/login")
async def login(
    login: str, password: str, auth_service: AuthService = Depends(get_auth_service)
) -> JSONResponse:
    token = await auth_service.login(login, password)

    if not token:
        return JSONResponse(
            content={"success": False, "error": "Invalid login or password"},
            status_code=401,
        )

    return JSONResponse(
        content={"success": True, "access_token": token, "token_type": "Bearer"},
        status_code=200,
    )


@auth_router.post("/test")
async def test(current_user_id: int = Depends(get_current_user_id)) -> JSONResponse:
    return JSONResponse({"success": True, "current_user_id": current_user_id})
