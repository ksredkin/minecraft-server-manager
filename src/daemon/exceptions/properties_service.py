from src.daemon.exceptions.server import MSMDaemonError


class PropertiesServiceError(MSMDaemonError):
    pass


class PropertiesFileNotFoundError(PropertiesServiceError):
    pass


class PropertiesFileReadError(PropertiesServiceError):
    pass


class PropertiesFileTypeError(PropertiesServiceError):
    pass


class InvalidPropertiesFileError(PropertiesServiceError):
    pass
