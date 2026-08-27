from fastapi import Depends
from src.api.services.payment_service import PaymentService
from src.api.services.subscription_service import SubscriptionService
from src.common.repositories.payment_repository import PaymentRepository
from src.common.repositories.subscription_repository import SubscriptionRepository
from src.api.dependencies.database import get_payment_repository
from src.api.api_clients.payments.interface import PaymentProvider
from src.api.api_clients.payments.yookassa import YooCassaProvider
from src.common.database.connection import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession


def get_yoocassa_provider() -> YooCassaProvider:
    return YooCassaProvider()


def get_payment_service(
    payment_repository: PaymentRepository = Depends(get_payment_repository),
    payment_provider: PaymentProvider = Depends(get_yoocassa_provider),
) -> PaymentService:
    return PaymentService(payment_repository, payment_provider)


def get_subscription_service(session: AsyncSession = Depends(get_db_session), payment_provider: PaymentProvider = Depends(get_yoocassa_provider)) -> SubscriptionService:
    return SubscriptionService(SubscriptionRepository(session), PaymentService(PaymentRepository(session), payment_provider))
