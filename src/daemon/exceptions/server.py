class MSMDaemonError(Exception):
    pass


class ServerError(MSMDaemonError):
    pass


class ServerIsAlreadyRunningError(ServerError):
    pass


class ServerIsNotRunningError(ServerError):
    pass


class ServerStopTimeoutError(ServerError):
    pass


class ServerFolderDoesNotExistError(ServerError):
    pass


class ServerJarDoesNotExistError(ServerError):
    pass


class ServerResponseTimeoutError(ServerError):
    pass
