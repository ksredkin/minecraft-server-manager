class MSMAPIError(Exception):
    status_code = 500


class ConfigurationError(MSMAPIError):
    status_code = 500
