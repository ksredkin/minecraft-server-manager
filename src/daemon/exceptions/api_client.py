from src.daemon.exceptions.server import MSMDaemonError


class APIClientError(MSMDaemonError):
    pass


class NoValidDaemonKeysError(APIClientError):
    pass
