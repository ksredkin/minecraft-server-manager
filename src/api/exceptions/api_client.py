from src.api.exceptions.api import MSMAPIError


class APIClientError(MSMAPIError):
    status_code = 502


class APIClientConnectionError(APIClientError):
    status_code = 503


class APIClientHttpError(APIClientError):
    status_code = 502


class APIClientNetworkError(APIClientError):
    status_code = 503


class APIClientProtocolError(APIClientError):
    status_code = 502


class APIClientTimeoutError(APIClientError):
    status_code = 504


class APIClientInvalidResponseError(APIClientError):
    status_code = 502
