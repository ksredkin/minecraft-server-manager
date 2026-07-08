from src.api.exceptions.server import MSMError


class BackupError(MSMError):
    pass


class InvalidBackupError(BackupError):
    pass


class BackupNotFoundError(BackupError):
    pass


class BackupPermisionError(BackupError):
    pass


class DiskSpaceError(BackupError):
    pass


class CleanupError(BackupError):
    pass


class BackupRestoreError(BackupError):
    pass
