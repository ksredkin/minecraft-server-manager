from enum import Enum


class CacheResultStatus(Enum):
    FOUND = "found"
    NOT_FOUND = "not_found"
    MISS = "miss"


class ServerUserRole(Enum):
    OWNER = "owner"
    ADMIN = "admin"
    VIEWER = "viewer"


class ActionStatus(Enum):
    SUCCESS = "action_completed"
    FAILED = "action_failed"
