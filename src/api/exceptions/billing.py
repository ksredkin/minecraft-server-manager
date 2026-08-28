from src.api.exceptions.api import MSMAPIError


class BillingError(MSMAPIError):
    pass


class NewPlanIsLowerThanCurrent(BillingError):
    pass


class PlanAlreadyActive(BillingError):
    pass


class ActiveSubscriptionNotFound(BillingError):
    pass


class PaymentInitializationError(BillingError):
    pass
