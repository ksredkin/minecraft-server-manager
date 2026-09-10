from src.daemon.exceptions.server import MSMDaemonError


class FileServiceError(MSMDaemonError):
    pass


class InvalidPathError(FileServiceError):
    pass


class ItemNotFoundError(FileServiceError):
    pass


class ItemAlreadyExistsError(FileServiceError):
    pass


class ItemTypeError(FileServiceError):
    pass


class FileReadError(FileServiceError):
    pass


class FileWriteError(FileServiceError):
    pass


class FolderReadError(FileServiceError):
    pass


class FolderWriteError(FileServiceError):
    pass


class ItemDeleteError(FileServiceError):
    pass

