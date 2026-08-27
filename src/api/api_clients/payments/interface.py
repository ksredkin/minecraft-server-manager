from abc import abstractmethod, ABC
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class PaymentResponse:
    external_payment_id: str
    status: str
    confirmation_url: str | None = None


class PaymentProvider(ABC):
    @abstractmethod
    def create(
        self, amount: Decimal, return_url: str, description: str
    ) -> PaymentResponse:
        pass

    @abstractmethod
    def get(self, payment_id: str) -> PaymentResponse:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass
