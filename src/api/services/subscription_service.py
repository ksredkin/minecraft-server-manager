from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.exc import IntegrityError

from src.api.exceptions.billing import (
    ActiveSubscriptionNotFound,
    NewPlanIsLowerThanCurrent,
    PaymentInitializationError,
    PlanAlreadyActive,
)
from src.api.services.payment_service import PaymentService
from src.common.billing.plans import PLANS
from src.common.database.models import Payment, Subscription
from src.common.enums import PaymentStatus, SubscriptionLevel, SubscriptionStatus
from src.common.repositories.subscription_repository import SubscriptionRepository


class SubscriptionService:
    def __init__(
        self,
        subscription_repository: SubscriptionRepository,
        payment_service: PaymentService,
    ) -> None:
        self.subscription_repository = subscription_repository
        self.payment_service = payment_service

    async def get_actual_subscription(self, user_id: int) -> Subscription | None:
        now = datetime.now(timezone.utc)

        subscription = await self.subscription_repository.get_active_by_user_id(user_id)
        if not subscription:
            return await self.subscription_repository.create(
                user_id, SubscriptionLevel.FREE, SubscriptionStatus.ACTIVE, now
            )

        actual_subscription: Subscription | None
        if subscription.end_at is not None and subscription.end_at < now:
            await self.subscription_repository.update_by_id(
                subscription.id, new_status=SubscriptionStatus.EXPIRED
            )
            try:
                actual_subscription = await self.subscription_repository.create(
                    user_id, SubscriptionLevel.FREE, SubscriptionStatus.ACTIVE, now
                )
            except IntegrityError:
                actual_subscription = (
                    await self.subscription_repository.get_active_by_user_id(user_id)
                )
        else:
            actual_subscription = subscription

        return actual_subscription

    async def get_user_cloud_backups_limit(self, user_id: int) -> int:
        subscription = await self.get_actual_subscription(user_id)
        if not subscription:
            return 0
        return PLANS[subscription.level].cloud_storage_gb

    async def create(
        self,
        user_id: int,
        plan: SubscriptionLevel,
        status: SubscriptionStatus,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
    ) -> Subscription:
        return await self.subscription_repository.create(
            user_id, plan, status, start_at, end_at
        )

    async def get_active(self, user_id: int) -> Subscription:
        active = await self.subscription_repository.get_active_by_user_id(user_id)
        if not active:
            raise ActiveSubscriptionNotFound("Active subscription not found.")
        return active

    async def checkout(
        self, user_id: int, checkout_plan: SubscriptionLevel
    ) -> str | None:
        active_subscription = await self.get_active(user_id)

        if active_subscription:
            if (
                active_subscription.level == SubscriptionLevel.ENTERPRISE
                and checkout_plan == SubscriptionLevel.PRO
                or active_subscription.level == SubscriptionLevel.PRO
                and checkout_plan == SubscriptionLevel.FREE
            ):
                raise NewPlanIsLowerThanCurrent(
                    "New plan cannot be lower then current plan."
                )

            if active_subscription.level == checkout_plan:
                raise PlanAlreadyActive("Plan is already active.")

        subscription = await self.create(
            user_id, checkout_plan, SubscriptionStatus.PENDING
        )

        payment_response = await self.payment_service.create(
            user_id, subscription.id, checkout_plan
        )

        if not payment_response:
            raise PaymentInitializationError(
                "Failed to create payment session with the provider."
            )

        return payment_response.confirmation_url

    async def handle_yookassa_webhook(self, data: dict[str, Any]) -> bool:
        event = data.get("event")
        payment_data = data.get("object")

        if not payment_data or not isinstance(payment_data, dict):
            return False

        payment_id = payment_data.get("id")

        if not payment_id:
            return False

        if event == "payment.succeeded":
            payment = (
                await self.payment_service.get_from_database_by_external_payment_id(
                    payment_id
                )
            )
            if not payment or not isinstance(payment, Payment):
                return False

            if payment.status == PaymentStatus.SUCCEEDED:
                return True

            yookassa_payment = self.payment_service.get_from_yookassa_by_payment_id(
                payment.external_payment_id
            )
            if yookassa_payment.status == "succeeded":
                now = datetime.now(timezone.utc)

                await self.payment_service.update_by_payment_id(
                    payment.id, new_status=PaymentStatus.SUCCEEDED, new_completed_at=now
                )

                payment_subscription = (
                    await self.subscription_repository.get_by_payment_id(payment.id)
                )
                if not isinstance(payment_subscription, Subscription):
                    return False

                actve_subscription = await self.get_active(payment_subscription.user_id)
                await self.subscription_repository.update_by_id(
                    actve_subscription.id,
                    new_status=SubscriptionStatus.EXPIRED,
                    new_end_at=now,
                )

                if not payment.subscription_id:
                    return False

                await self.subscription_repository.update_by_id(
                    payment.subscription_id,
                    new_status=SubscriptionStatus.ACTIVE,
                    new_start_at=now,
                    new_end_at=now + timedelta(days=30),
                )
                return True
            return False
        return True
