from src.api.exceptions.api import MSMAPIError


class ServerError(MSMAPIError):
    status_code = 500


class ServerNotFoundError(ServerError):
    status_code = 404


class ServerDoesNotHaveOwnerError(ServerError):
    status_code = 400
