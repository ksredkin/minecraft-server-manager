from src.api.services.jwt_service import JwtService
from src.api.services.user_service import UserService


class AuthService:
    def __init__(self, user_service: UserService, jwt_service: JwtService):
        self.user_service = user_service
        self.jwt_service = jwt_service

    async def register(
        self, login: str, password: str, email: str | None = None
    ) -> str | None:
        user = await self.user_service.create_user(login, password, email)

        if not user:
            return None

        return self.jwt_service.encode(user.id)

    async def login(self, login: str, password: str) -> str | None:
        user = await self.user_service.authenticate_user(login, password)

        if user is None:
            return None

        return self.jwt_service.encode(user.id)
