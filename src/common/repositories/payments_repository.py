from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database.models import Payment


class PaymentsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_payment(
        self,
        user_id: int,
        level: str,
        status: str,
        start_at: datetime,
        end_at: datetime,
    ) -> Payment:
        payment = Payment(
            user_id=user_id,
            level=level,
            status=status,
            start_at=start_at,
            end_at=end_at,
        )
        self.session.add(payment)
        await self.session.flush()
        return payment
