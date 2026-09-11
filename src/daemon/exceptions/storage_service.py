from src.daemon.exceptions.server import MSMDaemonError

class StorageServiceError(MSMDaemonError):
    pass


class StoragePathNotFoundError(StorageServiceError):
    pass


class StorageAccessError(StorageServiceError):
    pass


class ReservationNotFoundError(StorageServiceError):
    pass
