from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database.models import Subscription


class SubscriptionsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_subscription(
        self,
        user_id: int,
        subscription_id: int,
        provider: str,
        external_payment_id: str,
        amount: int,
        currency: str,
        status: str,
        completed_at: datetime | None = None,
    ) -> Subscription:
        subscription = Subscription(
            user_id=user_id,
            subscription_id=subscription_id,
            provider=provider,
            external_payment_id=external_payment_id,
            amount=amount,
            currency=currency,
            status=status,
            completed_at=completed_at,
        )
        self.session.add(subscription)
        await self.session.flush()
        return subscription
