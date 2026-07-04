class MSMError(Exception):
    pass


class ServerAlreadyRunningError(MSMError):
    pass


class ServerFolderDoesNotExistError(MSMError):
    pass


class InvalidServerConfigurationError(MSMError):
    pass


class ServerStopTimeoutError(MSMError):
    pass


class ServerNotRunningError(MSMError):
    pass


class ServerResponseTimeoutError(MSMError):
    pass
