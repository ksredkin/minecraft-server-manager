from src.api.services.password_service import PasswordService
from src.common.database.models import User
from src.common.repositories.user_repository import UserRespository


class UserService:
    def __init__(
        self, user_repository: UserRespository, password_service: PasswordService
    ):
        self.user_repository = user_repository
        self.password_service = password_service

    async def create_user(
        self,
        login: str,
        password: str,
        email: str | None = None,
        email_confirmed: bool = False,
    ) -> User | None:
        existing_user = await self.user_repository.get_user_by_login(login)

        if existing_user:
            return None

        password_hash = self.password_service.hash(password)
        return await self.user_repository.create_user(
            login, password_hash, email, email_confirmed
        )

    async def authenticate_user(self, login: str, password: str) -> User | None:
        user = await self.user_repository.get_user_by_login(login)

        if user is None:
            return None

        if not self.password_service.verify(user.password_hash, password):
            return None

        return user
