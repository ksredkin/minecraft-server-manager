from src.api.exceptions.api import MSMAPIError


class ServerError(MSMAPIError):
    pass


class ServerNotFoundError(ServerError):
    pass
