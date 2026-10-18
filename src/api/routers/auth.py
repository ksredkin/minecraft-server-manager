from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from src.api.dependencies.auth import get_auth_service, get_current_user_id, get_user_service
from src.api.services.auth_service import AuthService
from src.api.services.user_service import UserService

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
        secure=False,
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
        secure=False,
        samesite="lax",
        path="/",
    )

    return response


@auth_router.get("/me")
async def me(current_user_id: int = Depends(get_current_user_id), user_service: UserService = Depends(get_user_service)):
    user = await user_service.get_user(current_user_id)
    if not user:
        response = JSONResponse(content={"success": False, "error": "User associated with this token format or ID was not found."}, status_code=401)
        response.delete_cookie("access_token")
        return response
    
    return JSONResponse(content={"success": True, "user": {"login": user.login, "email": user.email, "email_confirmed": user.email_confirmed}}, status_code=200)



@auth_router.post("/exit")
async def exit():
    resp = JSONResponse(content={"success": True}, status_code=200)

    resp.delete_cookie(
        key="access_token", 
        path="/",
        httponly=True,
        samesite="lax",
        secure=False,
    )

    return resp
