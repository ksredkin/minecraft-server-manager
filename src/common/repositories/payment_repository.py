from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database.models import Payment
from src.common.enums import PaymentStatus

NOT_SET = object()


class PaymentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: int,
        subscription_id: int,
        provider: str,
        external_payment_id: str,
        amount: int,
        currency: str,
        status: PaymentStatus,
        completed_at: datetime | None = None,
    ) -> Payment:
        payment = Payment(
            user_id=user_id,
            subscription_id=subscription_id,
            provider=provider,
            external_payment_id=external_payment_id,
            amount=amount,
            currency=currency,
            status=status,
            completed_at=completed_at,
        )
        self.session.add(payment)
        await self.session.flush()
        return payment

    async def get_by_external_payment_id(
        self, external_payment_id: str
    ) -> Payment | None:
        result = await self.session.execute(
            select(Payment).where(Payment.external_payment_id == external_payment_id)
        )
        return result.scalar_one_or_none()

    async def update_by_payment_id(
        self,
        payment_id: int,
        new_status: PaymentStatus | object = NOT_SET,
        new_completed_at: datetime | object = NOT_SET,
    ) -> Payment | None:
        payment = await self.session.get(Payment, payment_id)
        if not payment:
            return None

        if isinstance(new_status, PaymentStatus):
            payment.status = new_status
        if isinstance(new_completed_at, datetime) or new_completed_at is None:
            payment.completed_at = new_completed_at

        await self.session.flush()
        return payment
