from src.api.exceptions.server import MSMError


class EulaError(MSMError):
    pass


class EulaFileNotFoundError(EulaError):
    pass


class EulaStatusNotFoundError(EulaError):
    pass
