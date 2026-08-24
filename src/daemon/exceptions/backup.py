from src.daemon.exceptions.server import MSMDaemonError


class BackupError(MSMDaemonError):
    pass


class BackupsFolderInServerFolderError(BackupError):
    pass


class BackupsFolderDoesNotExistError(BackupError):
    pass


class BackupPermissionError(BackupError):
    pass


class BackupRestoreError(BackupError):
    pass


class BackupNotFoundError(BackupError):
    pass


class InvalidBackupError(BackupError):
    pass


class CleanupError(BackupError):
    pass
