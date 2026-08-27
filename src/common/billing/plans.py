from src.common.enums import SubscriptionLevel, Feature
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Plan:
    level: SubscriptionLevel
    price: Decimal
    cloud_storage_gb: int
    features: list[Feature]


PLANS = {
    SubscriptionLevel.FREE: Plan(
        level=SubscriptionLevel.FREE, price=Decimal(0), cloud_storage_gb=0, features=[]
    ),
    SubscriptionLevel.PRO: Plan(
        level=SubscriptionLevel.PRO,
        price=Decimal(299),
        cloud_storage_gb=10,
        features=[],
    ),
    SubscriptionLevel.ENTERPRISE: Plan(
        level=SubscriptionLevel.ENTERPRISE,
        price=Decimal(1490),
        cloud_storage_gb=100,
        features=[],
    ),
}
