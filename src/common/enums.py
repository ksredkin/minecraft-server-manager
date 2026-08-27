from enum import Enum


class CacheResultStatus(Enum):
    FOUND = "found"
    NOT_FOUND = "not_found"
    MISS = "miss"


class ServerUserRole(Enum):
    OWNER = "owner"
    ADMIN = "admin"
    VIEWER = "viewer"


class DaemonRequestStatus(Enum):
    ACCEPTED = "request_accepted"
    SUCCESS = "request_completed"
    FAILED = "request_failed"


class TaskStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    ACCEPTED = "accepted"
    FAILED = "failed"


class SubscriptionLevel(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Feature(Enum):
    pass


class SubscriptionStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class PaymentStatus(Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    CANCELLED = "cancelled"
