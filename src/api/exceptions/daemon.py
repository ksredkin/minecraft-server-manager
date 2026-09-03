from src.api.exceptions.api import MSMAPIError


class DaemonError(MSMAPIError):
    pass


class DaemonDisconnectedError(DaemonError):
    pass


class InvalidDaemonResponseError(DaemonError):
    pass


class DaemonDiskFullError(DaemonError):
    pass
