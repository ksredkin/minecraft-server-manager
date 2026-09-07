from src.api.exceptions.api import MSMAPIError


class BackupError(MSMAPIError):
    status_code = 500


class NoFreeSpaceError(BackupError):
    status_code = 507


class BackupNotFoundError(BackupError):
    status_code = 404


class BackupCorruptedError(BackupError):
    status_code = 500
