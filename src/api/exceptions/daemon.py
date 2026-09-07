from src.api.exceptions.api import MSMAPIError


class DaemonError(MSMAPIError):
    status_code = 500


class DaemonDisconnectedError(DaemonError):
    status_code = 503


class InvalidDaemonResponseError(DaemonError):
    status_code = 500


class DaemonDiskFullError(DaemonError):
    status_code = 507
