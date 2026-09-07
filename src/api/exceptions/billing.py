from src.api.exceptions.api import MSMAPIError


class BillingError(MSMAPIError):
    status_code = 500


class NewPlanIsLowerThanCurrent(BillingError):
    status_code = 400


class PlanAlreadyActive(BillingError):
    status_code = 400


class ActiveSubscriptionNotFound(BillingError):
    status_code = 404


class PaymentInitializationError(BillingError):
    status_code = 500
