from decimal import Decimal
from uuid import uuid4

from yookassa import Configuration, Payment

from src.api.api_clients.payments.interface import PaymentProvider, PaymentResponse
from src.common.core.config import secrets, settings

Configuration.configure(settings.yookassa_shop_id, secrets.get("yookassa_secret_key"))


class YooKassaProvider(PaymentProvider):
    def create(
        self, amount: Decimal, return_url: str, description: str
    ) -> PaymentResponse:
        payment = Payment.create(
            {
                "amount": {
                    "value": amount,
                    "currency": "RUB",
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": return_url,
                },
                "capture": True,
                "description": description,
            },
            str(uuid4()),
        )
        return PaymentResponse(
            payment.id,
            payment.status,
            confirmation_url=(
                payment.confirmation.confirmation_url if payment.confirmation else None
            ),
        )

    def get(self, payment_id: str) -> PaymentResponse:
        payment = Payment.find_one(payment_id)
        return PaymentResponse(
            external_payment_id=str(payment.id),
            status=payment.status,
            confirmation_url=str(payment.confirmation.confirmation_url)
            if payment.confirmation
            else None,
        )

    def __str__(self) -> str:
        return "yookassa"
