from src.api.services.payment_service import PaymentService
from src.common.repositories.subscription_repository import SubscriptionRepository
from src.common.enums import SubscriptionLevel, SubscriptionStatus
from src.api.exceptions.billing import NewPlanIsLowerThanCurrent, PlanAlreadyActive, ActiveSubscriptionNotFound
from src.common.database.models import Subscription
from src.common.enums import PaymentStatus
from datetime import datetime, timezone, timedelta


class SubscriptionService:
    def __init__(self, subscription_repository: SubscriptionRepository, payment_service: PaymentService) -> None:
        self.subscription_repository = subscription_repository
        self.payment_service = payment_service

    async def create(self, user_id: int, plan: SubscriptionLevel, status: SubscriptionStatus, start_at: datetime|None = None, end_at: datetime|None = None) -> Subscription:
        return await self.subscription_repository.create(user_id, plan, status, start_at, end_at)

    async def get_active(self, user_id: int) -> Subscription:
        active = await self.subscription_repository.get_active_by_user_id(user_id)
        if not active:
            raise ActiveSubscriptionNotFound("Active subscription not found.")
        return active

    async def checkout(self, user_id: int, checkout_plan: SubscriptionLevel) -> str:
        active_subscription = await self.get_active(user_id)

        if active_subscription:
            if active_subscription.level == SubscriptionLevel.ENTERPRISE and checkout_plan == SubscriptionLevel.PRO or active_subscription.level == SubscriptionLevel.PRO and checkout_plan == SubscriptionLevel.FREE:
                raise NewPlanIsLowerThanCurrent("New plan cannot be lower then current plan.")

            if active_subscription.level == checkout_plan:
                raise PlanAlreadyActive("Plan is already active.")

        subscription = await self.create(user_id, checkout_plan, SubscriptionStatus.PENDING)

        payment_response = await self.payment_service.create(
            user_id, subscription.id, checkout_plan
        )

        return payment_response.confirmation_url

    async def handle_yookassa_webhook(self, data: dict[str, str|dict[str, str]]) -> bool:        
        event = data.get("event")
        payment_data = data.get("object")

        if not payment_data:
            return False

        payment_id = payment_data.get("id")

        if not payment_id:
            return False

        if event == "payment.succeeded":
            payment = await self.payment_service.get_from_database_by_external_payment_id(payment_id)
            if not payment:
                return False     

            if payment.status == "succeeded":
                return True

            yoocassa_payment = self.payment_service.get_from_yoocassa_by_payment_id(payment.external_payment_id)
            if yoocassa_payment.status == "succeeded":
                now = datetime.now(timezone.utc)

                await self.payment_service.update_by_payment_id(payment.id, new_status=PaymentStatus.SUCCEEDED, new_completed_at=now)

                payment_subscription = await self.subscription_repository.get_by_payment_id(payment.id)
                actve_subscription = await self.get_active(payment_subscription.user_id)
                await self.subscription_repository.update_by_id(actve_subscription.id, new_status=SubscriptionStatus.EXPIRED, new_end_at=now)

                await self.subscription_repository.update_by_id(payment.subscription_id, new_status=SubscriptionStatus.ACTIVE, new_start_at=now, new_end_at=now+timedelta(days=30))
                return True
            return False
        return True
