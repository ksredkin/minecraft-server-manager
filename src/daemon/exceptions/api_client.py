from src.daemon.exceptions.server import MSMDaemonError


class APIClientError(MSMDaemonError):
    pass


class NoValidDaemonKeysError(APIClientError):
    pass


class ApiClientConnectionError(APIClientError):
    pass


class ApiClientHttpError(APIClientError):
    pass


class ApiClientNetworkError(APIClientError):
    pass


class ApiClientProtocolError(APIClientError):
    pass


class ApiClientTimeoutError(APIClientError):
    pass


class ApiClientInvalidResponseError(APIClientError):
    pass
