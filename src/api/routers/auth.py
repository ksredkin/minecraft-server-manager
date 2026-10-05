from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from src.api.dependencies.auth import get_auth_service
from src.api.services.auth_service import AuthService

auth_router = APIRouter(prefix="/auth")


@auth_router.post("/register", description="Создать аккаунт.")
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

    response = JSONResponse(
        content={"success": True},
        status_code=201,
    )
    
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )
    
    return response


@auth_router.post("/login", description="Войти в аккаунт.")
async def login(
    login: str, password: str, auth_service: AuthService = Depends(get_auth_service)
) -> JSONResponse:
    token = await auth_service.login(login, password)

    if not token:
        return JSONResponse(
            content={"success": False, "error": "Invalid login or password"},
            status_code=401,
        )

    response = JSONResponse(
        content={"success": True},
        status_code=200,
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )

    return response
