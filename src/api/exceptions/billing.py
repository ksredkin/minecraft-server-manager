from src.api.exceptions.api import MSMAPIError


class NewPlanIsLowerThanCurrent(MSMAPIError):
    pass


class PlanAlreadyActive(MSMAPIError):
    pass


class ActiveSubscriptionNotFound(MSMAPIError):
    pass
