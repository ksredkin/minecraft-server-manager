from src.api.exceptions.server import MSMError


class ApiClientError(MSMError):
    pass


class ApiClientTimeoutError(ApiClientError):
    pass


class ApiClientConnectionError(ApiClientError):
    pass


class ApiClientProtocolError(ApiClientError):
    pass


class ApiClientNetworkError(ApiClientError):
    pass


class ApiClientHttpError(ApiClientError):
    pass


class ApiClientInvalidResponseError(ApiClientError):
    pass
