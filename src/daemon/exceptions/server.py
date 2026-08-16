class MSMDaemonError(Exception):
    pass


class ServerError(MSMDaemonError):
    pass


class ServerIsAlreadyRunningError(ServerError):
    pass


class ServerIsNotRunningError(ServerError):
    pass
