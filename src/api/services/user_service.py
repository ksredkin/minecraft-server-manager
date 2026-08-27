from src.api.services.password_service import PasswordService
from src.api.services.subscription_service import SubscriptionService
from src.common.database.models import User
from src.common.repositories.user_repository import UserRespository
from src.common.enums import SubscriptionLevel, SubscriptionStatus
from datetime import datetime, timezone


class UserService:
    def __init__(
        self, user_repository: UserRespository, password_service: PasswordService, subscription_service: SubscriptionService
    ):
        self.user_repository = user_repository
        self.password_service = password_service
        self.subscription_service = subscription_service

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
        user = await self.user_repository.create_user(
            login, password_hash, email, email_confirmed
        )
        await self.subscription_service.create(user.id, SubscriptionLevel.FREE, SubscriptionStatus.ACTIVE, datetime.now(timezone.utc))
        return user

    async def authenticate_user(self, login: str, password: str) -> User | None:
        user = await self.user_repository.get_user_by_login(login)

        if user is None:
            return None

        if not self.password_service.verify(user.password_hash, password):
            return None

        return user
