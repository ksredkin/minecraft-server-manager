from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database.models import Subscription, Payment
from src.common.enums import SubscriptionLevel, SubscriptionStatus
from sqlalchemy import select

NOT_SET = object()

class SubscriptionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: int,
        level: SubscriptionLevel,
        status: SubscriptionStatus,
        start_at: datetime|None = None,
        end_at: datetime|None = None,
    ) -> Subscription:
        subscription = Subscription(
            user_id=user_id,
            level=level,
            status=status,
            start_at=start_at,
            end_at=end_at,
        )
        self.session.add(subscription)
        await self.session.flush()
        return subscription

    async def get_active_by_user_id(self, user_id: int) -> Subscription|None:
        result = await self.session.execute(select(Subscription).where(Subscription.user_id == user_id, Subscription.status == SubscriptionStatus.ACTIVE))
        return result.scalar_one_or_none()

    async def get_by_payment_id(self, payment_id: int) -> Subscription|None:
        result = await self.session.execute(select(Subscription).join(Payment, Subscription.id == Payment.subscription_id).where(Payment.id == payment_id))
        return result.scalar_one_or_none()

    async def update_by_id(self, subscription_id: int, new_level: SubscriptionLevel|object = NOT_SET, new_status: SubscriptionStatus|object = NOT_SET, new_start_at: datetime|None|object = NOT_SET, new_end_at: datetime|None|object = NOT_SET) -> Subscription|None:
        subscription = await self.session.get(Subscription, subscription_id)
        if not subscription:
            return None

        if new_level is not NOT_SET:
            subscription.level = new_level

        if new_status is not NOT_SET:
            subscription.status = new_status

        if new_start_at is not NOT_SET:
            subscription.start_at = new_start_at

        if new_end_at is not NOT_SET:
            subscription.end_at = new_end_at

        await self.session.flush()
        return subscription
