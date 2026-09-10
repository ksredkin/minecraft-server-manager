from src.daemon.exceptions.server import MSMDaemonError


class EulaServiceError(MSMDaemonError):
    pass


class EulaFileNotFoundError(EulaServiceError):
    pass


class EulaFileReadError(EulaServiceError):
    pass


class InvalidEulaFileError(EulaServiceError):
    pass


class EulaFileUpdateError(EulaServiceError):
    pass
