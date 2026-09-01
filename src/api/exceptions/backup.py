from src.api.exceptions.api import MSMAPIError


class BackupError(MSMAPIError):
    pass


class NoFreeSpaceError(BackupError):
    pass


class BackupNotFoundError(BackupError):
    pass
