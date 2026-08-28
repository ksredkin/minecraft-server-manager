from datetime import datetime

from src.api.api_clients.payments.interface import PaymentProvider, PaymentResponse
from src.common.billing.plans import PLANS
from src.common.core.config import settings
from src.common.database.models import Payment
from src.common.enums import PaymentStatus, SubscriptionLevel
from src.common.repositories.payment_repository import NOT_SET, PaymentRepository


class PaymentService:
    def __init__(
        self, payment_repository: PaymentRepository, payment_provider: PaymentProvider
    ):
        self.payment_repository = payment_repository
        self.payment_provider = payment_provider

    async def create(
        self, user_id: int, subscription_id: int, plan: SubscriptionLevel
    ) -> PaymentResponse:
        price = PLANS[plan].price

        payment_response = self.payment_provider.create(
            price, settings.payment_return_url, f"MSM {str(plan)}"
        )
        if not payment_response.confirmation_url:
            return None

        await self.payment_repository.create(
            user_id,
            subscription_id,
            str(self.payment_provider),
            payment_response.external_payment_id,
            price * 100,
            "kopeck",
            PaymentStatus.PENDING,
        )
        return payment_response

    async def get_from_database_by_external_payment_id(
        self, external_payment_id: str
    ) -> Payment | None:
        return await self.payment_repository.get_by_external_payment_id(
            external_payment_id
        )

    async def update_by_payment_id(
        self,
        payment_id: str,
        new_status: PaymentStatus | object = NOT_SET,
        new_completed_at: datetime | object = NOT_SET,
    ) -> Payment | None:
        return await self.payment_repository.update_by_payment_id(
            payment_id, new_status=new_status, new_completed_at=new_completed_at
        )

    def get_from_yookassa_by_payment_id(self, payment_id: str) -> Payment | None:
        return self.payment_provider.get(payment_id)
